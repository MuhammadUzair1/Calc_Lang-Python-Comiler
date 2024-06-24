import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.tokens = []
        self.current_char = None
        self.pos = -1
        self.line = 1
        self.next_char()

    def next_char(self):
        self.pos += 1
        if self.pos >= len(self.input_text):
            self.current_char = None
        else:
            self.current_char = self.input_text[self.pos]
            if self.current_char == '\n':
                self.line += 1

    def tokenize(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.next_char()
            elif self.current_char.isdigit():
                self.tokens.append(('INTEGER', self.integer(), self.line))
            elif self.current_char == '+':
                self.tokens.append(('PLUS', '+', self.line))
                self.next_char()
            elif self.current_char == '-':
                self.tokens.append(('MINUS', '-', self.line))
                self.next_char()
            elif self.current_char == '*':
                self.tokens.append(('MUL', '*', self.line))
                self.next_char()
            elif self.current_char == '/':
                self.tokens.append(('DIV', '/', self.line))
                self.next_char()
            elif self.current_char == '(':
                self.tokens.append(('LPAREN', '(', self.line))
                self.next_char()
            elif self.current_char == ')':
                self.tokens.append(('RPAREN', ')', self.line))
                self.next_char()
            else:
                self.error()
        return self.tokens

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.next_char()
        return int(result)

    def error(self):
        raise Exception(f'Illegal character at line {self.line}')

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error()

    def error(self):
        raise Exception(f'Syntax error at line {self.current_token[2]}')

    def factor(self):
        token = self.current_token
        if token[0] == 'INTEGER':
            self.eat('INTEGER')
            return token[1]
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        elif token[0] == 'MINUS':
            self.eat('MINUS')
            return -self.factor()
        else:
            self.error()

    def term(self):
        result = self.factor()
        while self.current_token[0] in ('MUL', 'DIV'):
            token = self.current_token
            if token[0] == 'MUL':
                self.eat('MUL')
                result *= self.factor()
            elif token[0] == 'DIV':
                self.eat('DIV')
                divisor = self.factor()
                if divisor == 0:
                    raise Exception(f'Semantic error: Division by zero at line {token[2]}')
                result /= divisor
        return result

    def expr(self):
        result = self.term()
        while self.current_token[0] in ('PLUS', 'MINUS'):
            token = self.current_token
            if token[0] == 'PLUS':
                self.eat('PLUS')
                result += self.term()
            elif token[0] == 'MINUS':
                self.eat('MINUS')
                result -= self.term()
        return result

class CalcLangApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcLang Parser")
        self.create_widgets()

    def create_widgets(self):
        self.input_label = tk.Label(self.root, text="Expression / Factors", font=("Arial", 14), bg="lightblue")
        self.input_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.input_text = tk.Entry(self.root, font=("Arial", 12), width=50)
        self.input_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.run_button = tk.Button(self.root, text="RUN", font=("Arial", 12), command=self.run_expression)
        self.run_button.grid(row=2, column=0, padx=10, pady=10)

        self.clear_button = tk.Button(self.root, text="CLEAR", font=("Arial", 12), command=self.clear_input)
        self.clear_button.grid(row=2, column=1, padx=10, pady=10)

        self.result_label = tk.Label(self.root, text="Result", font=("Arial", 14), bg="lightgray")
        self.result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.result_text = tk.Text(self.root, height=2, width=40, font=("Arial", 12))
        self.result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.save_button = tk.Button(self.root, text="SAVE", font=("Arial", 12), command=self.save_output)
        self.save_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.semantic_label = tk.Label(self.root, text="Semantic Output", font=("Arial", 14), bg="lightblue")
        self.semantic_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        self.semantic_text = tk.Text(self.root, height=2, width=40, font=("Arial", 12))
        self.semantic_text.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.lexical_label = tk.Label(self.root, text="Lexical Output", font=("Arial", 14), bg="lightblue")
        self.lexical_label.grid(row=0, column=2, columnspan=2, padx=10, pady=10)

        columns = ('S No.', 'Token', 'Type', 'Line')
        self.lexical_tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.lexical_tree.heading(col, text=col)
            self.lexical_tree.column(col, width=100)
        self.lexical_tree.grid(row=1, column=2, rowspan=8, padx=10, pady=10)

    def run_expression(self):
        expression = self.input_text.get()
        self.result_text.delete('1.0', tk.END)
        self.semantic_text.delete('1.0', tk.END)
        for i in self.lexical_tree.get_children():
            self.lexical_tree.delete(i)

        try:
            lexer = Lexer(expression)
            tokens = lexer.tokenize()
            for i, token in enumerate(tokens):
                self.lexical_tree.insert('', tk.END, values=(i + 1, token[1], token[0], token[2]))

            parser = Parser(tokens)
            result = parser.expr()
            self.result_text.insert(tk.END, result)
        except Exception as e:
            error_message = str(e)
            if "Syntax error" in error_message or "Illegal character" in error_message:
                self.result_text.insert(tk.END, f"Error: {error_message}")
            elif "Semantic error" in error_message:
                self.semantic_text.insert(tk.END, f"Error: {error_message}")

    def clear_input(self):
        self.input_text.delete(0, tk.END)
        self.result_text.delete('1.0', tk.END)
        self.semantic_text.delete('1.0', tk.END)
        for i in self.lexical_tree.get_children():
            self.lexical_tree.delete(i)

    def save_output(self):
        input_text = self.input_text.get()
        result_text = self.result_text.get('1.0', tk.END).strip()
        semantic_text = self.semantic_text.get('1.0', tk.END).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"calc_output_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Input:\n{input_text}\n\n")
            f.write(f"Result:\n{result_text}\n\n")
            f.write(f"Semantic Output:\n{semantic_text}\n\n")
        messagebox.showinfo("Save Output", f"Output saved to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalcLangApp(root)
    root.mainloop()
