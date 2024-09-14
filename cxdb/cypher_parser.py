# cypher_parser.py

import ply.yacc as yacc
import logging
from cxdb.cypher_lexer import CypherLexer
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError, CypherParserError, CypherLexerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CypherParser:
    def __init__(self):
        self.lexer = CypherLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def p_query(self, p):
        '''query : match_clause where_clause return_clause'''
        p[0] = Query(p[1], p[2], p[3])

    def p_match_clause(self, p):
        '''match_clause : MATCH node_pattern'''
        p[0] = MatchClause(p[2])

    def p_node_pattern(self, p):
        '''node_pattern : LPAREN IDENTIFIER COLON IDENTIFIER RPAREN'''
        p[0] = NodePattern(p[2], p[4])

    def p_where_clause(self, p):
        '''where_clause : WHERE condition
                        | empty'''
        p[0] = WhereClause(p[2]) if len(p) > 2 else None

    def p_condition(self, p):
        '''condition : property_access EQUALS STRING'''
        p[0] = Condition(p[1], p[3])

    def p_property_access(self, p):
        '''property_access : IDENTIFIER DOT IDENTIFIER'''
        p[0] = PropertyAccess(p[1], p[3])

    def p_return_clause(self, p):
        '''return_clause : RETURN return_items
                         | RETURN error'''
        if len(p) == 3 and p[2] == 'error':
            raise CypherSyntaxError("Incomplete RETURN clause", p.lineno(1), p.lexpos(1), p[1])
        p[0] = ReturnClause(p[2])

    def p_return_items(self, p):
        '''return_items : return_item
                        | return_item COMMA return_items'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_return_item(self, p):
        '''return_item : IDENTIFIER
                       | IDENTIFIER AS IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER AS IDENTIFIER'''
        if len(p) == 2:
            p[0] = ReturnItem(p[1], p[1])
        elif len(p) == 4 and p[2] == 'AS':
            p[0] = ReturnItem(p[1], p[3])
        elif len(p) == 4 and p[2] == '.':
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", f"{p[1]}.{p[3]}")
        elif len(p) == 6:
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", p[5])

    def p_error(self, p):
        if p:
            raise CypherSyntaxError(f"Syntax error", p.lineno, p.lexpos, p.value)
        else:
            raise CypherSyntaxError("Syntax error at EOF", None, None, None)


    def parse(self, data):
        try:
            return self.parser.parse(data, lexer=self.lexer.lexer)
        except CypherLexerError as e:
            logger.error(f"Lexer error at position {e.position}: {e.message}")
            print(f"Lexer error at position {e.position}: {e.message}")
            print(f"Context:\n{self._get_error_context(data, e.position)}")
            raise
        except CypherSyntaxError as e:
            if e.line and e.column:
                logger.error(f"Syntax error at line {e.line}, column {e.column}: {e.message}")
                print(f"Syntax error at line {e.line}, column {e.column}: {e.message}")
            else:
                logger.error(f"Syntax error: {e.message}")
                print(f"Syntax error: {e.message}")
            raise
        except CypherSemanticError as e:
            logger.error(f"Semantic error: {str(e)}")
            print(f"Semantic error: {str(e)}")
            raise
        except CypherParserError as e:
            logger.error(f"Parser error: {str(e)}")
            print(f"Parser error: {str(e)}")
            raise
        except Exception as e:
            logger.exception("Unexpected error occurred during parsing")
            print(f"Unexpected error: {str(e)}")
            raise

    def _get_error_context(self, data, position, context_length=20):
        start = max(0, position - context_length)
        end = min(len(data), position + context_length)
        context = data[start:end]
        pointer = ' ' * (position - start) + '^'
        return f"{context}\n{pointer}"

# AST node classes
class Query:
    def __init__(self, match, where, return_):
        self.match = match
        self.where = where
        self.return_ = return_

class MatchClause:
    def __init__(self, pattern):
        self.pattern = pattern

class NodePattern:
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

class WhereClause:
    def __init__(self, condition):
        self.condition = condition

class Condition:
    def __init__(self, property_access, value):
        self.property_access = property_access
        self.value = value

class PropertyAccess:
    def __init__(self, identifier, property):
        self.identifier = identifier
        self.property = property
        
class ReturnClause:
    def __init__(self, items):
        self.items = items

class ReturnItem:
    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias