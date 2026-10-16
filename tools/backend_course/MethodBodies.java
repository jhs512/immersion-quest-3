import javax.tools.*;
import com.sun.source.util.*;
import com.sun.source.tree.*;
class MethodBodies {
    public static void main(String[] args) throws Exception {
        var compiler=ToolProvider.getSystemJavaCompiler();
        try (var files=compiler.getStandardFileManager(null,null,java.nio.charset.StandardCharsets.UTF_8)) {
            var task=(JavacTask)compiler.getTask(null,files,null,java.util.List.of("-proc:none"),null,files.getJavaFileObjects(args[0]));
            var tree=task.parse().iterator().next();
            var positions=Trees.instance(task).getSourcePositions();
            new TreeScanner<Void,Void>() {
                public Void visitMethod(MethodTree node,Void ignored) {
                    // Constructors retain initialization and remain in the scaffold.
                    if(node.getReturnType()!=null && node.getBody()!=null)
                        System.out.println(positions.getStartPosition(tree,node.getBody())+":"+positions.getEndPosition(tree,node.getBody()));
                    return null;
                }
            }.scan(tree,null);
        }
    }
}
