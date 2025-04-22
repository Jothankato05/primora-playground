from pygls.server import LanguageServer
from lsprotocol.types import TEXT_DOCUMENT_DID_OPEN, Diagnostic, DiagnosticSeverity, Position, Range

server = LanguageServer('primora-lsp', '0.1')

@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params):
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = []
    
    # Basic error checking (e.g., invalid keywords)
    lines = text_doc.source.splitlines()
    for i, line in enumerate(lines):
        if 'invalid_keyword' in line:  # Mock error detection
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=i, character=0),
                    end=Position(line=i, character=len(line))
                ),
                message="Invalid keyword detected",
                severity=DiagnosticSeverity.Error
            ))
    
    ls.publish_diagnostics(text_doc.uri, diagnostics)

if __name__ == '__main__':
    server.start_tcp('localhost', 8080)
