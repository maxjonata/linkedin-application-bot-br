import tkinter as tk
from tkinter import ttk
import utils

class AnswerUnansweredQuestions(tk.Tk):
    def __init__(self):
        self.root = tk.Tk.__init__(self)
        self.buttons = []  # Lista para armazenar os botões
        self.current_button = 0  # Índice do botão atualmente selecionado
        self.errorsList = utils.getErrorsListFromJson()
        self.totalQuestions = len(self.errorsList)
        self.currentQuestionIndex = 0
        self.title("Answer Larissa")
        self.frame = tk.Frame(self)
        self.frame.pack()
        self.create_widgets()

    def create_widgets(self):
        # Fecha se chegou no ultimo erro
        if self.currentQuestionIndex == self.totalQuestions:
            self.quit()
            return
        # Barra de progresso no topo
        self.progressBar = ttk.Progressbar(self.frame, length=300, mode='determinate')
        self.progressBar.pack()
        self.update_progress_bar()

        # Label com a contagem de perguntas
        self.questionCountLabel = tk.Label(self.frame, text=f"Questão {self.currentQuestionIndex+1} de {self.totalQuestions}")
        self.questionCountLabel.pack()

        # Title as the question
        question = self.errorsList[self.currentQuestionIndex]["Label"]
        self.questionLabel = tk.Label(self.frame, text=question)
        self.questionLabel.pack()

        if "Options" in self.errorsList[self.currentQuestionIndex]:
            options = self.errorsList[self.currentQuestionIndex]["Options"]
            self.create_options(options)
        else:
            self.create_textbox()

    def create_textbox(self):
        # make a textbox that sends answered value to answer() when pressing enter
        self.answerEntry = tk.Entry(self.frame)
        self.answerEntry.bind("<Return>", lambda event: self.answer(self.answerEntry.get()))
        self.answerEntry.pack()
        self.answerEntry.focus_set()

    def create_options(self, options):
        # Shows all options as buttons that saves the answered value when pressed
        for option in options:
            button = tk.Button(self.frame, text=option, command=lambda option=option: self.answer(option))
            button.pack(side="left", anchor="center")
            self.buttons.append(button)
        # Vincula os eventos de teclado
        self.bind('<Left>', self.previous_button)
        self.bind('<Right>', self.next_button)
        self.bind('<Up>', self.previous_button)
        self.bind('<Down>', self.next_button)
        

        for i in range(len(self.buttons)):
            self.bind(str(i+1), lambda event, i=i: self.buttons[i].invoke())

        self.bind('<Return>', self.press_button)

        self.buttons[self.current_button].focus_set()

    def previous_button(self, event):
        # Move o foco para o botão anterior
        self.current_button = (self.current_button - 1) % len(self.buttons)
        self.buttons[self.current_button].focus_set()

    def next_button(self, event):
        # Move o foco para o próximo botão
        self.current_button = (self.current_button + 1) % len(self.buttons)
        self.buttons[self.current_button].focus_set()

    def press_button(self, event):
        # "Pressiona" o botão atualmente focado
        print(f"Botão {self.current_button+1} pressionado")
        self.buttons[self.current_button].invoke()

    def answer(self, answer):
        # save the answer in self.answeredQuestion as {question: Label, answer: Answer}
        utils.saveAnsweredQuestion({"question":self.errorsList[self.currentQuestionIndex]["Label"], "answer": answer})
        self.currentQuestionIndex += 1
        # Destroy the old frame and create a new one
        self.buttons = []
        self.unbind_all('')
        self.frame.destroy()
        self.frame = tk.Frame(self)
        self.frame.pack()
        self.create_widgets()
    
    def update_progress_bar(self):
        # Atualiza a barra de progresso com base no índice da pergunta atual.
        progress = (self.currentQuestionIndex / self.totalQuestions) * 100
        self.progressBar['value'] = progress

    def main(self):
        self.mainloop()

if __name__ == "__main__":
    # Execute the tkinter app
    app = AnswerUnansweredQuestions()
    app.main()

    # Converte todas as respostas em config_local textQuestionAnswers radioQuestionAnswers e selectQuestionAnswers para dentro do answeredQuestions.json
    # for question in config_local.textQuestionAnswers:
    #     utils.saveAnsweredQuestion({question: config_local.textQuestionAnswers[question]})
    # for question in config_local.radioQuestionAnswers:
    #     utils.saveAnsweredQuestion({question: config_local.radioQuestionAnswers[question]})
    # for question in config_local.selectQuestionAnswers:
    #     utils.saveAnsweredQuestion({question: config_local.selectQuestionAnswers[question]})