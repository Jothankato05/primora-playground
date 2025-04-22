# Minimal stub lexer and parser for Primora language

class PrimoraLexer:
    def tokenize(self, code):
        # For simplicity, return code split by lines as tokens
        return code.strip().splitlines()

class PrimoraParser:
    def parse(self, tokens):
        # Improved parse: handle blocks for if-else and nested statements
        ast = []
        i = 0
        while i < len(tokens):
            line = tokens[i].strip()
            if line.startswith("plot"):
                # Syntax: plot <var> as <title>
                parts = line.split(' as ')
                var = parts[0][5:].strip()
                title = parts[1].strip().strip('"')
                ast.append(('plot', var, title))
                i += 1
                continue
            if line.startswith("email"):
                # Syntax: email to <address> subject <subject> body <body>
                import re
                to = re.search(r'to\s+([\w@.\-]+)', line)
                subject = re.search(r'subject\s+"([^"]+)"', line)
                body = re.search(r'body\s+"([^"]+)"', line)
                ast.append(('email', to.group(1) if to else '', subject.group(1) if subject else '', body.group(1) if body else ''))
                i += 1
                continue
            if line.startswith("automate"):
                # Syntax: automate <action> on <target>
                parts = line.split(' on ')
                action = parts[0][9:].strip()
                target = parts[1].strip() if len(parts) > 1 else ''
                ast.append(('automate', action, target))
                i += 1
                continue
            if line.startswith("search"):
                # Syntax: search "<query>" as <var>
                parts = line.split(' as ')
                query = parts[0][7:].strip().strip('"')
                var = parts[1].strip()
                ast.append(('search', query, var))
                i += 1
                continue
            if line.startswith("summarize"):
                # Syntax: summarize <var> as <summary_var>
                parts = line.split(' as ')
                target_var = parts[0][10:].strip()
                summary_var = parts[1].strip()
                ast.append(('summarize', target_var, summary_var))
                i += 1
                continue
            if line.startswith("fetch"):
                # Syntax: fetch url("<url>") as <var>
                parts = line.split()
                url_part = parts[1]
                var = parts[-1]
                url = url_part[url_part.find('("')+2:url_part.find('")')]
                ast.append(('fetch', (None, url), var))
                i += 1
                continue
            if line.startswith("listen"):
                parts = line.split()
                source = parts[1]
                var = parts[-1]
                url = source[source.find('("')+2:source.find('")')]
                ast.append(('listen', (None, url), var))
                i += 1
            elif line.startswith("predict"):
                parts = line.split()
                var = parts[1]
                expr = parts[3]
                model_part = parts[-1]
                model_name = model_part[model_part.find('("')+2:model_part.find('")')]
                ast.append(('predict', var, (None, expr), (None, model_name)))
                i += 1
            elif line.startswith("if"):
                # Parse if condition and blocks
                cond_start = line.find('(')+1
                cond_end = line.find(')')
                cond = line[cond_start:cond_end]
                if '.' in cond:
                    expr, method_value = cond.split('.', 1)
                    if '(' in method_value:
                        method, value = method_value.split('(', 1)
                        value = value.strip('")')
                    else:
                        method = method_value
                        value = ""
                else:
                    expr = cond
                    method = ""
                    value = ""
                then_block = []
                else_block = []
                i += 1
                # Parse then block
                if i < len(tokens) and tokens[i].strip() == '{':
                    i += 1
                    while i < len(tokens) and tokens[i].strip() != '}':
                        then_block.append(tokens[i].strip())
                        i += 1
                    i += 1  # skip closing '}'
                # Check for else block
                if i < len(tokens) and tokens[i].strip().startswith('else'):
                    i += 1
                    if i < len(tokens) and tokens[i].strip() == '{':
                        i += 1
                        while i < len(tokens) and tokens[i].strip() != '}':
                            else_block.append(tokens[i].strip())
                            i += 1
                        i += 1  # skip closing '}'
                # Recursively parse then and else blocks
                from copy import deepcopy
                then_ast = PrimoraParser().parse(deepcopy(then_block))
                else_ast = PrimoraParser().parse(deepcopy(else_block)) if else_block else []
                ast.append(('if', (None, expr), method, f'"{value}"', then_ast, else_ast))
            elif line.startswith("manipulate"):
                parts = line.split()
                var = parts[1]
                tactic_part = line[line.find('tactic(')+7:line.find(')')]
                tactic_items = tactic_part.split(',')
                tactic_name = tactic_items[0].strip().strip('"')
                tone = tactic_items[1].split('=')[1].strip().strip('"') if len(tactic_items) > 1 else ""
                ast.append(('manipulate', var, (None, tactic_name, tone)))
                i += 1
            elif line.startswith("echo"):
                parts = line.split('using')
                message_part = parts[0].strip()[5:].strip().strip('"')
                frame_part = parts[1].strip()
                frame_name = frame_part[frame_part.find('("')+2:frame_part.find('")')]
                ast.append(('echo', (None, message_part), (None, frame_name)))
                i += 1
            else:
                i += 1
        return ast
