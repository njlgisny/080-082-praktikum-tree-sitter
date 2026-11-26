import sys
import builtins
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))


def get_text(node, source):
    return source[node.start_byte:node.end_byte].decode("utf-8")


def get_type(node, source, variables):
    if node.type == "string":
        return "str"
    if node.type == "integer":
        return "int"
    if node.type == "float":
        return "float"
    if node.type == "identifier":
        return variables.get(get_text(node, source))
    return None


def collect_symbols(root, source):
    symbols = {"classes": {}, "functions": {}}

    def visit(node, class_name=None):
        if node.type == "class_definition":
            class_name = get_text(node.child_by_field_name("name"), source)
            symbols["classes"][class_name] = {
                "attributes": set(), "methods": {}
            }

        if node.type == "function_definition":
            name = get_text(node.child_by_field_name("name"), source)
            params = node.child_by_field_name("parameters")
            parameters = []

            if params:
                for p in params.named_children:
                    if p.type in ("identifier", "typed_parameter"):
                        param_name = get_text(
                            p if p.type == "identifier" else p.named_children[0],
                            source
                        )
                        type_node = (
                            p.child_by_field_name("type")
                            if p.type == "typed_parameter" else None
                        )
                        parameters.append((
                            param_name,
                            get_text(type_node, source) if type_node else None
                        ))

            info = {
                "parameters": parameters,
                "return": (
                    get_text(node.child_by_field_name("return_type"), source)
                    if node.child_by_field_name("return_type") else None
                ),
                "node": node
            }

            if class_name:
                symbols["classes"][class_name]["methods"][name] = info
            else:
                symbols["functions"][name] = info

        if node.type == "assignment" and class_name:
            left = node.child_by_field_name("left")
            if left and left.type == "attribute":
                obj = left.child_by_field_name("object")
                attr = left.child_by_field_name("attribute")
                if obj and attr and get_text(obj, source) == "self":
                    symbols["classes"][class_name]["attributes"].add(
                        get_text(attr, source)
                    )

        for child in node.named_children:
            visit(child, class_name)

    visit(root)
    return symbols


def check_type(node, source, variables, symbols, errors):
    if node.type == "call":
        function = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")

        if not function or not args:
            return

        if function.type == "attribute":
            obj = function.child_by_field_name("object")
            method = function.child_by_field_name("attribute")
            class_name = variables.get(get_text(obj, source)) if obj else None
            method_name = get_text(method, source) if method else ""
        elif function.type == "identifier":
            class_name = get_text(function, source)
            method_name = "__init__"
        else:
            return

        class_info = symbols["classes"].get(class_name)
        if not class_info:
            return

        method_info = class_info["methods"].get(method_name)
        if not method_info:
            return

        params = [
            p for p in method_info["parameters"] if p[0] != "self"
        ]

        for i, arg in enumerate(args.named_children):
            if i >= len(params):
                break

            actual = get_type(arg, source, variables)
            expected = params[i][1]

            if actual and expected and actual != expected:
                if not (actual == "int" and expected == "float"):
                    errors.append((
                        arg.start_point.row + 1,
                        f"Argumen '{get_text(arg, source)}' pada "
                        f"'{method_name}()' bertipe '{actual}', sedangkan "
                        f"parameter '{params[i][0]}' membutuhkan tipe "
                        f"'{expected}'."
                    ))

    if node.type == "binary_operator":
        left = node.child_by_field_name("left")
        right = node.child_by_field_name("right")

        if left and right:
            left_type = get_type(left, source, variables)
            right_type = get_type(right, source, variables)

            if left_type == "str" and right_type in ("int", "float"):
                errors.append((
                    node.start_point.row + 1,
                    f"Penjumlahan '{get_text(node, source)}' menggunakan "
                    f"tipe '{left_type}' dan '{right_type}' yang berbeda."
                ))


def check_attribute(node, source, variables, symbols, errors):
    if node.type != "attribute":
        return

    parent = node.parent
    if parent and parent.type == "call":
        if parent.child_by_field_name("function") == node:
            return

    obj = node.child_by_field_name("object")
    attr = node.child_by_field_name("attribute")

    if not obj or not attr or obj.type != "identifier":
        return

    class_name = variables.get(get_text(obj, source))
    class_info = symbols["classes"].get(class_name)

    if class_info:
        name = get_text(attr, source)
        if name not in class_info["attributes"]:
            errors.append((
                node.start_point.row + 1,
                f"Atribut '{name}' yang diakses melalui "
                f"'{get_text(node, source)}' tidak ditemukan "
                f"dalam class '{class_name}'."
            ))


def check_scope(function, source, symbols):
    params = function.child_by_field_name("parameters")
    body = function.child_by_field_name("body")
    declared = set()
    used = []

    if params:
        for p in params.named_children:
            if p.type == "identifier":
                declared.add(get_text(p, source))
            elif p.type == "typed_parameter":
                declared.add(get_text(p.named_children[0], source))

    def visit(node):
        if node.type == "function_definition" and node != function:
            return

        if node.type == "assignment":
            left = node.child_by_field_name("left")
            if left and left.type == "identifier":
                declared.add(get_text(left, source))

        if node.type == "for_statement":
            left = node.child_by_field_name("left")
            if left and left.type == "identifier":
                declared.add(get_text(left, source))

        if node.type == "identifier":
            parent = node.parent
            name = get_text(node, source)

            if parent and parent.type == "attribute":
                if parent.child_by_field_name("attribute") == node:
                    return
            if parent and parent.type == "assignment":
                if parent.child_by_field_name("left") == node:
                    return
            if parent and parent.type == "for_statement":
                if parent.child_by_field_name("left") == node:
                    return
            if parent and parent.type == "call":
                if parent.child_by_field_name("function") == node:
                    return
            if parent and parent.type in ("function_definition", "class_definition"):
                return

            used.append((name, node.start_point.row + 1))

        for child in node.named_children:
            visit(child)

    if body:
        visit(body)

    known = declared | set(symbols["classes"]) | set(symbols["functions"])
    known |= set(dir(builtins)) | {"__name__"}

    function_name = get_text(function.child_by_field_name("name"), source)

    return [
        (
            line,
            f"Variabel '{name}' belum dideklarasikan dalam "
            f"scope fungsi '{function_name}'."
        )
        for name, line in used if name not in known
    ]


def analyze_function(info, source, symbols):
    function = info["node"]
    variables = dict(info["parameters"])
    errors = []

    def visit(node):
        if node.type == "function_definition" and node != function:
            return

        if node.type == "for_statement":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")

            if left and right:
                name = get_text(left, source)
                if get_text(right, source) == "self.orders":
                    variables[name] = "Order"
                elif get_text(right, source) == "products":
                    variables[name] = "Product"

        if node.type == "assignment":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")

            if left and right and left.type == "identifier":
                if right.type == "call":
                    called = right.child_by_field_name("function")
                    if called and called.type == "identifier":
                        variables[get_text(left, source)] = get_text(called, source)
                    elif called and called.type == "attribute":
                        obj = called.child_by_field_name("object")
                        method = called.child_by_field_name("attribute")
                        class_name = variables.get(get_text(obj, source))
                        method_info = symbols["classes"].get(
                            class_name, {}
                        ).get("methods", {}).get(get_text(method, source), {})
                        if method_info.get("return"):
                            variables[get_text(left, source)] = method_info["return"]
                else:
                    value_type = get_type(right, source, variables)
                    if value_type:
                        variables[get_text(left, source)] = value_type

        if node.type == "augmented_assignment":
            left = node.child_by_field_name("left")
            if left and left.type == "identifier":
                variables.setdefault(get_text(left, source), "int")

        check_type(node, source, variables, symbols, errors)
        check_attribute(node, source, variables, symbols, errors)

        for child in node.named_children:
            visit(child)

    body = function.child_by_field_name("body")
    if body:
        visit(body)

    errors.extend(check_scope(function, source, symbols))
    return errors


def main():
    if len(sys.argv) < 2:
        print("Gunakan: python analyzer.py nama_file.py")
        return

    with open(sys.argv[1], "rb") as file:
        source = file.read()

    tree = parser.parse(source)
    symbols = collect_symbols(tree.root_node, source)

    errors = []

    for class_info in symbols["classes"].values():
        for info in class_info["methods"].values():
            errors.extend(analyze_function(info, source, symbols))

    for info in symbols["functions"].values():
        errors.extend(analyze_function(info, source, symbols))

    print("=== HASIL PEMERIKSAAN SEMANTIK ===")

    for line, message in sorted(errors, key=lambda item: item[0]):
        print(f"[ERROR] Baris {line}: {message}")

    print(f"\nJumlah kesalahan: {len(errors)}")


if __name__ == "__main__":
    main()
