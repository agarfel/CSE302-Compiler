#! /usr/bin/env python3

# --------------------------------------------------------------------
tokens = (
  'IDENT',
  'NUMBER',
  'PLUS',
  'MINUS',
  'STAR',
  'SLASH',
  'EQUAL',
  'LPAREN',
  'RPAREN',
)

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_STAR    = r'\*'
t_SLASH   = r'/'
t_EQUAL   = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_IDENT   = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# --------------------------------------------------------------------
precedence = (
  ('left' , 'PLUS', 'MINUS'),
  ('left' , 'STAR', 'SLASH'),
  ('right', 'UMINUS'),
)

# dictionary of names
names = { }

def p_statement_assign(t):
    'statement : IDENT EQUAL expression'
    names[t[1]] = t[3]

def p_statement_expr(t):
    'statement : expression'
    print(t[1])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression STAR expression
                  | expression SLASH expression'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_ident(t):
    'expression : IDENT'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_error(t):
    print("Syntax error at '%s'" % t.value)

# --------------------------------------------------------------------
import ply.yacc as yacc
parser = yacc.yacc()

# --------------------------------------------------------------------
def _main():
  while True:
    try:
      s = input('calc > ')   # Use raw_input on Python 2
    except EOFError:
      break
    parser.parse(s)

# --------------------------------------------------------------------
if __name__ == '__main__':
  _main()
