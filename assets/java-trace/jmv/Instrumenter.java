package jmv;

import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Set;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.IincInsnNode;
import org.objectweb.asm.tree.InsnList;
import org.objectweb.asm.tree.InsnNode;
import org.objectweb.asm.tree.JumpInsnNode;
import org.objectweb.asm.tree.LabelNode;
import org.objectweb.asm.tree.LdcInsnNode;
import org.objectweb.asm.tree.LineNumberNode;
import org.objectweb.asm.tree.LocalVariableNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.objectweb.asm.tree.TryCatchBlockNode;
import org.objectweb.asm.tree.VarInsnNode;

/**
 * Inserts {@link Tracer} hooks into user classes compiled by ECJ with debug attributes.
 *
 * Hooks: method entry (after super()/this() for constructors), parameter and local stores,
 * local scope end, source line entry, normal return, and a catch-all handler that records an
 * escaping exception and rethrows it unchanged. Field and array writes need no hook because
 * each snapshot reads the heap reachable from the stack and static roots.
 */
public final class Instrumenter implements Opcodes {
    static final String TRACER = "jmv/Tracer";
    final Map<String, byte[]> classes; // internal name -> original bytes, for hierarchy queries

    public Instrumenter(Map<String, byte[]> classesByBinaryName) {
        this.classes = new java.util.HashMap<>();
        for (Map.Entry<String, byte[]> e : classesByBinaryName.entrySet()) classes.put(e.getKey().replace('.', '/'), e.getValue());
    }

    static MethodInsnNode call(String name, String desc) { return new MethodInsnNode(INVOKESTATIC, TRACER, name, desc, false); }

    static void box(InsnList b, Type t) {
        String owner;
        switch (t.getSort()) {
            case Type.OBJECT: case Type.ARRAY: return;
            case Type.BOOLEAN: owner = "java/lang/Boolean"; break;
            case Type.BYTE: owner = "java/lang/Byte"; break;
            case Type.CHAR: owner = "java/lang/Character"; break;
            case Type.SHORT: owner = "java/lang/Short"; break;
            case Type.INT: owner = "java/lang/Integer"; break;
            case Type.LONG: owner = "java/lang/Long"; break;
            case Type.FLOAT: owner = "java/lang/Float"; break;
            case Type.DOUBLE: owner = "java/lang/Double"; break;
            default: throw new IllegalArgumentException(t.toString());
        }
        b.add(new MethodInsnNode(INVOKESTATIC, owner, "valueOf", "(" + t.getDescriptor() + ")L" + owner + ";", false));
    }

    static Type storeType(int opcode) {
        switch (opcode) {
            case ISTORE: return Type.INT_TYPE;
            case LSTORE: return Type.LONG_TYPE;
            case FSTORE: return Type.FLOAT_TYPE;
            case DSTORE: return Type.DOUBLE_TYPE;
            default: return Type.getType(Object.class);
        }
    }

    /** Finds the debug variable live at (or declared right after) an instruction for a slot. */
    static LocalVariableNode local(MethodNode m, AbstractInsnNode insn, int slot) {
        int pos = m.instructions.indexOf(insn);
        LocalVariableNode future = null;
        if (m.localVariables == null) return null;
        for (LocalVariableNode v : m.localVariables) {
            if (v.index != slot) continue;
            int start = m.instructions.indexOf(v.start), end = m.instructions.indexOf(v.end);
            if (start <= pos && pos < end) return v;
            if (start > pos && start - pos <= 3 && (future == null || start < m.instructions.indexOf(future.start))) future = v;
        }
        return future;
    }

    static void localHook(InsnList b, LocalVariableNode v, int slot, Type fallback) {
        if (v == null) return; // unnamed slot: nothing to show
        Type type = Type.getType(v.desc);
        b.add(new LdcInsnNode(v.name));
        b.add(new LdcInsnNode(v.desc));
        b.add(new VarInsnNode(type.getOpcode(ILOAD), slot));
        box(b, type);
        b.add(call("local", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V"));
    }

    public byte[] transform(byte[] bytes) {
        ClassNode c = new ClassNode();
        new ClassReader(bytes).accept(c, 0);
        for (MethodNode m : c.methods) {
            if ((m.access & (ACC_ABSTRACT | ACC_NATIVE)) != 0 || m.instructions.size() == 0) continue;
            AbstractInsnNode[] original = m.instructions.toArray();
            boolean constructor = m.name.equals("<init>");
            AbstractInsnNode anchor = original[0];
            int entryLine = 0;
            if (constructor) {
                anchor = null;
                for (AbstractInsnNode x : original) {
                    if (x instanceof LineNumberNode && anchor == null) entryLine = ((LineNumberNode) x).line;
                    if (x instanceof MethodInsnNode) {
                        MethodInsnNode v = (MethodInsnNode) x;
                        if (v.getOpcode() == INVOKESPECIAL && v.name.equals("<init>") && (v.owner.equals(c.superName) || v.owner.equals(c.name))) {
                            anchor = x.getNext(); break;
                        }
                    }
                }
                if (anchor == null) continue; // unusual constructor shape: leave uninstrumented
            }
            Set<AbstractInsnNode> active = Collections.newSetFromMap(new IdentityHashMap<>());
            boolean started = false;
            for (AbstractInsnNode x : original) { if (x == anchor) started = true; if (started) active.add(x); }

            InsnList entry = new InsnList();
            entry.add(new LdcInsnNode(c.name));
            entry.add(new LdcInsnNode(m.name));
            entry.add(new LdcInsnNode(Type.getObjectType(c.name)));
            if ((m.access & ACC_STATIC) == 0) entry.add(new VarInsnNode(ALOAD, 0)); else entry.add(new InsnNode(ACONST_NULL));
            entry.add(call("enter", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Class;Ljava/lang/Object;)V"));
            int slot = (m.access & ACC_STATIC) == 0 ? 1 : 0;
            boolean entryPoint = (m.access & ACC_STATIC) != 0 && m.name.equals("main") && m.desc.equals("([Ljava/lang/String;)V");
            if (!entryPoint) // the launcher passes an empty args array; showing it only adds noise
                for (Type arg : Type.getArgumentTypes(m.desc)) { localHook(entry, local(m, anchor, slot), slot, arg); slot += arg.getSize(); }
            if (constructor && entryLine > 0) { entry.add(new LdcInsnNode(entryLine)); entry.add(call("line", "(I)V")); }
            LabelNode start = new LabelNode();
            entry.add(start);
            m.instructions.insertBefore(anchor, entry);

            for (AbstractInsnNode x : original) {
                if (!active.contains(x)) continue;
                int op = x.getOpcode();
                if (x instanceof LineNumberNode) {
                    InsnList b = new InsnList();
                    b.add(new LdcInsnNode(((LineNumberNode) x).line));
                    b.add(call("line", "(I)V"));
                    m.instructions.insert(x, b);
                } else if (x instanceof VarInsnNode && op >= ISTORE && op <= ASTORE) {
                    VarInsnNode v = (VarInsnNode) x; InsnList b = new InsnList();
                    localHook(b, local(m, x, v.var), v.var, storeType(op));
                    if (b.size() > 0) m.instructions.insert(x, b);
                } else if (x instanceof IincInsnNode) {
                    IincInsnNode v = (IincInsnNode) x; InsnList b = new InsnList();
                    localHook(b, local(m, x, v.var), v.var, Type.INT_TYPE);
                    if (b.size() > 0) m.instructions.insert(x, b);
                } else if (x instanceof LabelNode && m.localVariables != null) {
                    InsnList b = new InsnList();
                    for (LocalVariableNode v : m.localVariables) if (v.end == x) {
                        b.add(new LdcInsnNode(v.name));
                        b.add(call("scopeEnd", "(Ljava/lang/String;)V"));
                    }
                    if (b.size() > 0) m.instructions.insert(x, b);
                } else if (x instanceof JumpInsnNode && m.instructions.indexOf(((JumpInsnNode) x).label) < m.instructions.indexOf(x)) {
                    m.instructions.insertBefore(x, call("tick", "()V")); // loop back-edge
                } else if (op >= IRETURN && op <= RETURN) {
                    InsnList b = new InsnList();
                    Type t = Type.getReturnType(m.desc);
                    if (op == RETURN) b.add(new InsnNode(ACONST_NULL));
                    else { b.add(new InsnNode(t.getSize() == 2 ? DUP2 : DUP)); box(b, t); }
                    b.add(new LdcInsnNode(t.getDescriptor()));
                    b.add(call("ret", "(Ljava/lang/Object;Ljava/lang/String;)V"));
                    m.instructions.insertBefore(x, b);
                }
            }
            LabelNode end = new LabelNode(), handler = new LabelNode();
            m.instructions.add(end);
            m.instructions.add(handler);
            m.instructions.add(new InsnNode(DUP));
            m.instructions.add(call("exceptionExit", "(Ljava/lang/Throwable;)V"));
            m.instructions.add(new InsnNode(ATHROW));
            m.tryCatchBlocks.add(new TryCatchBlockNode(start, end, handler, "java/lang/Throwable"));
            m.maxStack += 4;
        }
        ClassWriter writer = new ClassWriter(ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS) {
            @Override protected String getCommonSuperClass(String a, String b) { return commonSuperClass(a, b); }
        };
        c.accept(writer);
        return writer.toByteArray();
    }

    // ---- hierarchy resolution without loading user classes ----------------------------------

    String superName(String internal) {
        byte[] bytes = classes.get(internal);
        if (bytes != null) return new ClassReader(bytes).getSuperName();
        try {
            Class<?> k = Class.forName(internal.replace('/', '.'), false, Instrumenter.class.getClassLoader());
            return k.getSuperclass() == null ? null : k.getSuperclass().getName().replace('.', '/');
        } catch (ClassNotFoundException e) { return "java/lang/Object"; }
    }

    boolean isInterface(String internal) {
        byte[] bytes = classes.get(internal);
        if (bytes != null) return (new ClassReader(bytes).getAccess() & ACC_INTERFACE) != 0;
        try { return Class.forName(internal.replace('/', '.'), false, Instrumenter.class.getClassLoader()).isInterface(); }
        catch (ClassNotFoundException e) { return false; }
    }

    String commonSuperClass(String a, String b) {
        if (a.equals(b)) return a;
        if (isInterface(a) || isInterface(b)) return "java/lang/Object";
        java.util.List<String> chain = new java.util.ArrayList<>();
        for (String k = a; k != null; k = superName(k)) chain.add(k);
        for (String k = b; k != null; k = superName(k)) if (chain.contains(k)) return k;
        return "java/lang/Object";
    }
}
