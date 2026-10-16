"""JDK compiler-tree mutation plus executable API contracts (no text matching)."""


def contract(owner, method, replacement, checks):
    return '''class QuestContract {
    public static void main(String[] args) throws Exception {
        CHECKS
        String source = java.nio.file.Files.readString(java.nio.file.Path.of("Main.java"));
        var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
        try (var files = compiler.getStandardFileManager(null, null, java.nio.charset.StandardCharsets.UTF_8)) {
            var task = (com.sun.source.util.JavacTask) compiler.getTask(null, files, null,
                java.util.List.of("-proc:none"), null, files.getJavaFileObjects("Main.java"));
            var tree = task.parse().iterator().next();
            var positions = com.sun.source.util.Trees.instance(task).getSourcePositions();
            long[] bounds = {-1, -1};
            String[] change = {"REPLACEMENT"};
            new com.sun.source.util.TreeScanner<Void, String>() {
                public Void visitClass(com.sun.source.tree.ClassTree node, String parent) {
                    return super.visitClass(node, node.getSimpleName().toString());
                }
                public Void visitMethod(com.sun.source.tree.MethodTree node, String parent) {
                    if ("OWNER".equals(parent) && "METHOD".contentEquals(node.getName()) && node.getBody() != null) {
                        if (bounds[0] != -1) throw new AssertionError("검사할 메서드는 하나만 정의하세요.");
                        bounds[0] = positions.getStartPosition(tree, node.getBody());
                        bounds[1] = positions.getEndPosition(tree, node.getBody());
                    }
                    return super.visitMethod(node, parent);
                }
                public Void visitVariable(com.sun.source.tree.VariableTree node, String parent) {
                    if ("OWNER".equals(parent) && ("var:" + node.getName()).equals("METHOD")) {
                        if (node.getInitializer() != null) {
                            bounds[0] = positions.getStartPosition(tree, node.getInitializer());
                            bounds[1] = positions.getEndPosition(tree, node.getInitializer());
                        } else {
                            // Java fields without an initializer have a defined default.
                            bounds[0] = positions.getEndPosition(tree, node) - 1;
                            bounds[1] = bounds[0];
                            change[0] = " = " + change[0];
                        }
                    }
                    return super.visitVariable(node, parent);
                }
            }.scan(tree, "");
            if (bounds[0] < 0) throw new AssertionError("필요한 메서드를 정의하세요.");
            System.out.print(source.substring(0, (int) bounds[0]) + change[0] + source.substring((int) bounds[1]));
        }
    }
    static void require(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
}
'''.replace("CHECKS", checks).replace("OWNER", owner).replace("METHOD", method).replace("REPLACEMENT", replacement)
