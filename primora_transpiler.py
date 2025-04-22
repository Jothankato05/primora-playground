from primora_parser import PrimoraLexer, PrimoraParser

class PrimoraTranspiler:
    def __init__(self):
        self.output = []
        self.indent_level = 0

    def indent(self):
        return "    " * self.indent_level

    def transpile(self, ast):
        self.output = ["from primora_stdlib import primora_ai, primora_sec, primora_psy, primora_net"]
        self.output.append("variables = {}")
        for stmt in ast:
            self.transpile_stmt(stmt)

        return "\n".join(self.output)

    def transpile_stmt(self, stmt):
        stmt_type = stmt[0]
        if stmt_type == 'fetch':
            _, url, var = stmt
            self.output.append(f"{self.indent()}variables['{var}'] = primora_net.fetch_json('{url[1]}')")
        elif stmt_type == 'listen':
            _, source, var = stmt
            self.output.append(f"{self.indent()}variables['{var}'] = primora_sec.scan('{source[1]}')")
        elif stmt_type == 'predict':
            _, var, expr, model = stmt
            self.output.append(f"{self.indent()}variables['{var}'] = primora_ai.predict(variables.get('{expr[1]}', ''), '{model[1]}')")
        elif stmt_type == 'manipulate':
            _, var, tactic = stmt
            self.output.append(f"{self.indent()}primora_psy.manipulate(variables.get('{var}', '{var}'), '{tactic[1]}', '{tactic[2]}')")
        elif stmt_type == 'if':
            _, expr, method, value, then_block, else_block = stmt
            self.output.append(f"{self.indent()}if variables.get('{expr[1]}', {{}}).get('{method}', '') == {value}:")
            self.indent_level += 1
            for stmt in then_block:
                self.transpile_stmt(stmt)
            self.indent_level -= 1
            if else_block:
                self.output.append(f"{self.indent()}else:")
                self.indent_level += 1
                for stmt in else_block:
                    self.transpile_stmt(stmt)
                self.indent_level -= 1
        elif stmt_type == 'echo':
            _, message, frame = stmt
            self.output.append(f"{self.indent()}print(f'Echo: {message[1]} (frame: {frame[1]})')")

if __name__ == '__main__':
    lexer = PrimoraLexer()
    parser = PrimoraParser()
    transpiler = PrimoraTranspiler()
    code = '''
    listen source("http://intel.api") as data
    predict intent of data using ai.model("machiavelli")
    if intent.is("hostile") {
        manipulate subject using tactic("mirroring", tone="defensive")
    } else {
        echo "Situation safe" using frame("neutral")
    }
    '''
    tokens = lexer.tokenize(code)
    ast = parser.parse(tokens)
    python_code = transpiler.transpile(ast)
    print(python_code)
