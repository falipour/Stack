# -*- coding: utf-8 -*-
import csv
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

class Question:
    all_Questions = []

    def __init__(self, Id, CreationDate, Score, ViewCount, Body, OwnerUserId, Title, Tags, AnswerCount, CommentCount,AcceptedAnswerId):
        self.Id = Id
        self.CreationDate = CreationDate
        self.Score = Score
        self.ViewCount = ViewCount
        self.Body = Body
        self.OwnerUserId = OwnerUserId
        self.Title = Title
        self.Tags = Tags
        self.AnswerCount = AnswerCount
        self.CommentCount = CommentCount
        self.tag_similarity = 0
        self.Tags = self.Tags.split('<')
        for i in range(len(self.Tags)):
            self.Tags[i] = self.Tags[i][:-1]
        del self.Tags[0]
        self.question_asked = 0
        self.answered = 0
        self.AcceptedAnswerId=AcceptedAnswerId
        #if AnswerCount and int(AnswerCount) > 0:
         #   self.answered = 1
        if AcceptedAnswerId:
            self.answered=1
    def set_feature(self):
        self.title_length = len(self.Title)
        self.post_length = self.Body
        if self.Id != '40004818' and self.Id != '40037764' and self.Id != '7980583' and self.Id != '7980751':
            while '<code>' in self.post_length:
                index_code = self.post_length.index('<code>')
                index_end_code = self.post_length.index('</code>')
                self.post_length = self.post_length[:index_code] + self.post_length[index_end_code + 7:]
            self.post_length = len(self.post_length)

        for tag in self.Tags:
            for q in Question.all_Questions:
                if q != self and tag in q.Tags:
                    self.tag_similarity += 1
        self.code = 0
        if '<code>' in self.Body:
            self.code = 1
        for q in Question.all_Questions:
            if q != self and self.OwnerUserId == q.OwnerUserId:
                self.question_asked += 1
        self.asker_score = 0
        for u in Karbar.all_Users:
            if u.Id == self.OwnerUserId:
                self.asker_score = u.asker_score

    @staticmethod
    def asddQuestions(Question):
        Question.all_Questions.append(Question)


class Karbar:
    all_Users = []

    def __init__(self, Id, UpVotes, DownVotees):
        self.Id = Id
        self.UpVotes = UpVotes
        self.DownVotes = DownVotees

    def set_feature(self):
        self.asker_score = abs(int(self.UpVotes) - int(self.DownVotes))

    @staticmethod
    def addUser(User):
        User.all_Users.append(User)


with open('QueryResults.csv', 'rt') as file:
    reader = csv.reader(file)
    i = 0
    for row in reader:
        i += 1
        if i == 1002:
            break
        if i == 1:
            pass
        else:
            Question.asddQuestions(
                Question(row[0], row[4], row[6], row[7], row[8], row[9], row[15], row[16], row[17], row[18],row[2]))

with open('QueryResultsUser.csv', 'rt') as file:
    reader = csv.reader(file)
    i = 0
    for row in reader:
        i += 1
        if i == 1:
            pass
        else:
            Karbar.addUser(
                Karbar(row[0], row[9], row[10]))

for u in Karbar.all_Users:
    u.set_feature()
for q in Question.all_Questions:
    q.set_feature()
matrix_list = []
label = []
for q in Question.all_Questions[:800]:
    temp_list = []
    temp_list.append(q.title_length)
    temp_list.append(q.post_length)
    temp_list.append(q.tag_similarity)
    temp_list.append(q.code)
    temp_list.append(q.question_asked)
    temp_list.append(q.asker_score)
    matrix_list.append(temp_list)
    label.append(q.answered)
label_test = []
matrix_list_test = []
for q in Question.all_Questions[800:]:
    temp_list = []
    temp_list.append(q.title_length)
    temp_list.append(q.post_length)
    temp_list.append(q.tag_similarity)
    temp_list.append(q.code)
    temp_list.append(q.question_asked)
    temp_list.append(q.asker_score)
    matrix_list_test.append(temp_list)
    label_test.append(q.answered)

A = csr_matrix(matrix_list)
v = np.array(label)
A_test = csr_matrix(matrix_list_test)
#clf = RandomForestClassifier(max_depth=4, random_state=0)
clf = DecisionTreeClassifier(max_depth=4,random_state=0)
clf.fit(A, v)
predicted = clf.predict(A_test)

tp_answered = 0
fp_answered = 0
fn_answered = 0
tn_answered = 0

tp_unanswered = 0
fp_unanswered = 0
fn_unanswered = 0
tn_unanswered = 0

for i in range(len(predicted)):
    predicted_ans = predicted[i]
    if predicted_ans == 1 and label_test[i] == 1:
        tp_answered += 1
    if predicted_ans == 1 and label_test[i] != 1:
        fp_answered += 1
    if predicted_ans != 1 and label_test[i] == 1:
        fn_answered += 1
    if predicted_ans != 1 and label_test[i] != 1:
        tn_answered += 1
print tp_answered+tn_answered+fp_answered+fn_answered
precision_answered = tp_answered / float(tp_answered + fp_answered)
recall_answered = tp_answered / float(tp_answered + fn_answered)
f1_answered = (2 * precision_answered * recall_answered) / (recall_answered + precision_answered)
print 'Precision: ', precision_answered
print 'Recall: ', recall_answered
print 'F1: ', f1_answered

for i in range(len(predicted)):
    predicted_ans = predicted[i]
    if predicted_ans == 0 and label_test[i] == 0:
        tp_unanswered += 1
    if predicted_ans == 0 and label_test[i] != 0:
        fp_unanswered += 1
    if predicted_ans != 0 and label_test[i] == 0:
        fn_unanswered += 1
    if predicted_ans != 0 and label_test[i] != 0:
        tn_unanswered += 1

precision_unanswered = tp_unanswered / float(tp_unanswered + fp_unanswered)
recall_unanswered = tp_unanswered / float(tp_unanswered + fn_unanswered)
f1_unanswered = (2 * precision_unanswered * recall_unanswered) / (recall_unanswered + precision_unanswered)
print 'Precision: ', precision_unanswered
print 'Recall: ', recall_unanswered
print 'F1: ', f1_unanswered

print 'fianl F1: ',(f1_unanswered + f1_answered) / 2
