from primora_stdlib import primora_ai, primora_sec, primora_psy, primora_net, primora_web, primora_plot, primora_mail, primora_auto
import re
import requests

class PrimoraInterpreter:
    def __init__(self):
        self.variables = {}
        self.ai = primora_ai
        self.sec = primora_sec
        self.psy = primora_psy
        self.net = primora_net
        self.web = primora_web

    def sanitize_source(self, source):
        # Basic URL validation (expand with real security checks)
        if not re.match(r'^https?://[a-zA-Z0-9\./]+$', source):
            raise ValueError(f"Invalid source: {source}")
        return source

    def review_code(self, ast):
        # Mock AI-assisted code review (replace with real analysis)
        for stmt in ast:
            if stmt[0] == 'listen' and 'malicious' in stmt[1][1].lower():
                raise ValueError("Potential malicious source detected")
        return True

    def interpret(self, ast):
        if self.review_code(ast):
            for stmt in ast:
                self.execute_stmt(stmt)

    def execute_stmt(self, stmt):
        stmt_type = stmt[0]
        if stmt_type == 'plot':
            _, var, title = stmt
            data = self.variables.get(var, [])
            result = primora_plot.plot(data, title)
            print(result)
        elif stmt_type == 'email':
            _, to, subject, body = stmt
            result = primora_mail.send_email(to, subject, body)
            print(result)
        elif stmt_type == 'automate':
            _, action, target = stmt
            result = primora_auto.automate(action, target)
            print(result)
        elif stmt_type == 'search':
            _, query, var = stmt
            result = self.web.search_web(query)
            print(f"Searched the web for '{query}' and stored as {var}: {result}")
            self.variables[var] = result
        elif stmt_type == 'summarize':
            _, target_var, summary_var = stmt
            text = self.variables.get(target_var, "")
            if isinstance(text, list):
                text = ' '.join(text)
            result = self.web.summarize_text(text)
            print(f"Summarized {target_var} and stored as {summary_var}: {result}")
            self.variables[summary_var] = result
        elif stmt_type == 'fetch':
            _, url, var = stmt
            result = self.net.fetch_json(url[1])
            print(f"Fetched JSON from {url[1]} and stored as {var}: {result}")
            self.variables[var] = result
        elif stmt_type == 'listen':
            _, source, var = stmt
            sanitized_source = self.sanitize_source(source[1])
            result = self.sec.scan(sanitized_source)
            print(f"Listening to {sanitized_source} and storing as {var}: {result}")
            self.variables[var] = result
        elif stmt_type == 'predict':
            _, var, expr, model = stmt
            data = self.variables.get(expr[1], "")
            # If data is dict, convert to string for prediction
            if isinstance(data, dict):
                data_str = str(data)
            else:
                data_str = data
            result = self.ai.predict(data_str, model[1])
            print(f"Predicting {var} of {expr[1]} using model {model[1]}: {result}")
            self.variables[var] = result
        elif stmt_type == 'manipulate':
            _, var, tactic = stmt
            subject = self.variables.get(var, var)
            result = self.psy.manipulate(subject, tactic[1], tactic[2])
            print(f"Manipulating {subject} with tactic {tactic[1]} (tone: {tactic[2]}): {result}")
        elif stmt_type == 'wiki':
            _, query = stmt
            try:
                resp = requests.post('http://localhost:5001/wiki', json={'query': query})
                data = resp.json()
                print(f"Wikipedia summary for {query}: {data.get('extract', 'No result.')}")
            except Exception as e:
                print(f"Wiki error: {e}")
        elif stmt_type == 'weather':
            _, location = stmt
            try:
                resp = requests.post('http://localhost:5001/weather', json={'location': location})
                data = resp.json()
                print(f"Weather for {location}: {data.get('weather', 'No result.')}")
            except Exception as e:
                print(f"Weather error: {e}")
        elif stmt_type == 'news':
            _, topic = stmt
            try:
                resp = requests.post('http://localhost:5001/news', json={'topic': topic})
                data = resp.json()
                print(f"News for {topic}: {data.get('news', 'No result.')}")
            except Exception as e:
                print(f"News error: {e}")
        elif stmt_type == 'summarize_text':
            _, text = stmt
            try:
                resp = requests.post('http://localhost:5001/summarize', json={'text': text})
                data = resp.json()
                print(f"Summary: {data.get('summary', 'No result.')}")
            except Exception as e:
                print(f"Summarize error: {e}")
        elif stmt_type == 'if':
            _, expr, method, value, then_block, else_block = stmt
            condition_var = self.variables.get(expr[1], {})
            condition = condition_var.get(method, "") == value.strip('"')
            print(f"Checking if {expr[1]}.{method} is {value}: {condition}")
            if condition:
                for stmt in then_block:
                    self.execute_stmt(stmt)
            elif else_block:
                for stmt in else_block:
                    self.execute_stmt(stmt)
        elif stmt_type == 'echo':
            _, message, frame = stmt
            print(f"Echo: {message[1]} (frame: {frame[1]})")

if __name__ == '__main__':
    from primora_parser import PrimoraLexer, PrimoraParser
    lexer = PrimoraLexer()
    parser = PrimoraParser()
    interpreter = PrimoraInterpreter()
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
    interpreter.interpret(ast)
