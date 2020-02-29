#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

import json, hashlib,re

userList = []
objectsList = []


class AccessControl():
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self._load_users_data()
        self._load_config()

    def access_request(self):
        '''
        accessRequest rise an input dialog requesting user and password, if those exist and application is on TRIAL or
        PURCHASED app will run normally otherwise will rise the message: user name/pass is expired or license has
         expired, and close
        :return: nothing
        '''
        access_data = self._load_users_data()
        access_request = AccessRequest()

        user, password = access_request.get_user_input()

        if user and password:
            h_user = self._hashing(user)
            h_pass = self._hashing(password)
            for register in access_data:
                if register['user'] == h_user:
                    for register in access_data:
                        if register['pass'] == h_pass:
                            print('user name=%s' % register['name'], 'surname=%s' % register['surname'])
                            return True

    def save_config(self):
        pass

    def user_register(self):
        register_form = UserRegister()
        register_form.get_data_register()

    def _hashing(self, string):
        string = string.encode("utf-8")
        return hashlib.md5(string).hexdigest()

    def _load_config(self):
        '''
        loadConfig looks for config file and read it if exists, if not it creates one
        :return:
        '''
        try:
            with open('config.json', 'r') as _file:
                _config = json.load(_file)
                i = 0
                for item in _config['point']:
                    '''pp = pprint.PrettyPrinter()
                    pp.pprint(item)'''
                    i += 1
        except IOError:
            with open('config.json', 'w') as _file:
                json.dump(_config, _file, indent=4)

    def _load_users_data(self):
        # TODO: implement json load file from local host or web db idle
        '''
        loadUsers try to look up for a file with users enabled to use the application.
        if no file is found, it will try to connect to web server to look up for one.
        if data is located in the cloud, if'll download and create access_data.json for futures login.
        if no data cloud is allocated, it will ask for registration to create TRIAL data on the cloud.
        :return: nothing
        '''
        #print("loading users...")
        pp = pprint.PrettyPrinter()
        try:
            with open('access_data.json', 'r') as _file:
                #print("loading file...")
                _access_data = json.load(_file)
                for item in _access_data:
                    pp.pprint(item['user'])
                return _access_data
        except IOError:
                #print("users file doesn't exist...\n"
                #     "connecting with server")
                sheet = self.client.open('credentials').sheet1
                _access_data = sheet.get_all_records()
                if _access_data:
                    #print("connection done... access data collected")
                    with open('access_data.json', 'w') as _file:
                        json.dump(_access_data, _file, indent=4)
                        #print("file created successfully!")
                    pp = pprint.PrettyPrinter()
                    pp.pprint(_access_data)
                return _access_data


class AccessRequestGO(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)

        # Create a frame to place the form
        frame = QGroupBox("Login")
        self.setWindowTitle("Access Request")
        # Create form layout
        form = QFormLayout()

        # Create an add a full row [user, line edit] to layout
        user_lbl = QLabel("User name")

        self.user_val = QLineEdit()
        form.addRow(user_lbl, self.user_val)

        # Create an add a full row [password, line edit] to layout
        pass_lbl = QLabel("Password")

        self.pass_val = QLineEdit()
        self.pass_val.setObjectName('pass')
        self.pass_val.setEchoMode(QLineEdit.Password)
        self.pass_val.setToolTip("Supported password have to accomplish: \n"
                                 "> more than eight (8) characters\n"
                                 "> at least one (1) number\n"
                                 "> at least one (1) capital case")
        form.addRow(pass_lbl, self.pass_val)

        vbox = QVBoxLayout()
        button_box = QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(button_box)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        vbox.addLayout(form)
        vbox.addWidget(self.buttonBox)
        frame.setLayout(vbox)
        box = QHBoxLayout()
        box.addWidget(frame)
        self.setLayout(box)


class AccessRequest(AccessRequestGO):
    def __init__(self):
        super(AccessRequest, self).__init__()

    def get_user_input(self):
        if self.exec_() == QDialog.Accepted:
            if len(self.user_val.text()) > 0 and len(self.pass_val.text()) > 0:
                return self.user_val.text(), self.pass_val.text()
        else:
            return None, None


class UserRegisterGO(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)

        self.form_dict = []

        frame = QGroupBox()
        self.setWindowTitle("Registration")
        form = QFormLayout()

        company_lbl = QLabel("Company name")
        self.form_dict.append(company_lbl.text())
        self.company_name_val = QLineEdit()
        form.addRow(company_lbl,self.company_name_val)

        user_name_lbl = QLabel("Name")
        self.form_dict.append(user_name_lbl.text())
        self.user_name_val = QLineEdit()
        form.addRow(user_name_lbl, self.user_name_val)

        user_surname_lbl = QLabel("Surname")
        self.form_dict.append(user_surname_lbl.text())
        self.user_surname_val = QLineEdit()
        form.addRow(user_surname_lbl, self.user_surname_val)

        email_lbl = QLabel("Email")
        self.form_dict.append(email_lbl.text())
        self.email_val = QLineEdit()
        self.email_val.setObjectName('email')
        self.email_val.textChanged.connect(self._check_if_email)
        form.addRow(email_lbl, self.email_val)

        r_email_lbl = QLabel("Repeat email")
        self.r_email_val = QLineEdit()
        self.r_email_val.setObjectName('r_email')
        self.r_email_val.textChanged.connect(self._check_if_email)
        form.addRow(r_email_lbl, self.r_email_val)

        user_lbl = QLabel("User name")
        self.form_dict.append(user_lbl.text())
        self.user_val = QLineEdit()
        form.addRow(user_lbl, self.user_val)

        pass_lbl = QLabel("Password")
        self.form_dict.append(pass_lbl.text())
        self.pass_val = QLineEdit()
        self.pass_val.setObjectName('pass')
        self.pass_val.setEchoMode(QLineEdit.Password)
        self.pass_val.textChanged.connect(self._check_if_pass)
        self.pass_val.setToolTip("Supported password have to accomplish: \n"
                                 "> more than eight (8) characters\n"
                                 "> at least one (1) number\n"
                                 "> at least one (1) capital case")
        form.addRow(pass_lbl, self.pass_val)

        r_pass_lbl = QLabel("Repeat password")
        self.r_pass_val = QLineEdit()
        self.r_pass_val.setObjectName('r_pass')
        self.r_pass_val.setEchoMode(QLineEdit.Password)
        self.r_pass_val.textChanged.connect(self._check_if_pass)
        form.addRow(r_pass_lbl, self.r_pass_val)

        current_version_lbl = QLabel("Current version")
        self.form_dict.append(current_version_lbl.text())
        self.current_version_val = QLabel("Demo")
        form.addRow(current_version_lbl, self.current_version_val)

        vbox = QVBoxLayout()
        form_buttons = QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        self.buttonBox = QDialogButtonBox(form_buttons)
        self.buttonBox.clicked.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        vbox.addLayout(form)
        vbox.addWidget(self.buttonBox)
        frame.setLayout(vbox)
        box = QHBoxLayout()
        box.addWidget(frame)
        self.setLayout(box)


class UserRegister(UserRegisterGO):
    def __init__(self):
        super(UserRegister, self).__init__()

    def confirm_register(self):
        if self.exec_() == QDialog.Accepted:
            # TODO: implement a dict return of
            return self.user_val.text(), self.pass_val.text()
        else:
            return None

    def _check_if_email(self):
        '''
        this method check in runtime if the given email accomplish with the rule
         by looking for re.search method specify
        and if it matches with confirmed email
        :return: -1 if the email doesn't accomplish the rule,
        0 if accomplish the rule and 1 if both given emails match
        '''
        flag = 0
        if not re.search("[@.]", self.email_val.text()):
            flag = -1
            #print("email isn't ok")
            return flag
        if not re.search("com", self.email_val.text()):
            flag = -1
            #print("email isn't ok")
            return flag
        elif flag == 0:
            #print("email is ok")
            if self.email_val.text() == self.r_email_val.text():
                flag = 1
                #print("email match")
                return flag
            else:
                #print("email doesn't match")
                return

    def _check_if_pass(self):
        '''
        this method check if the given password accomplish with the rule by looking for re.search method specify
        :return: True for positive check
                False for negative check
        '''
        if len(self.pass_val.text()) < 8:
            return False
        elif not re.search("[a-z]", self.pass_val.text()):
            return False
        elif not re.search("[A-Z]", self.pass_val.text()):
            return False
        elif not re.search("[0-9]", self.pass_val.text()):
            return False
        elif re.search("\s", self.pass_val.text()):
            return False
        if self.pass_val.text() == self.r_pass_val.text():
            return True

    def _check_if_full(self):
        '''this method check if length of QLineEdit widget text are greater than 0,
         if at least one were 0 it's break and rise the request to full all data requested
         :return: True if valid data is filled, False if a required field is empty'''

        if not len(self.company_name_val.text()) > 0:
            return False
        elif not len(self.user_name_val.text()) > 0:
            return False
        elif not len(self.user_surname_val.text()) > 0:
            return False
        elif not len(self.user_val.text()) > 0:
            return False
        elif not self._check_if_email():
            return False
        elif not self._check_if_pass():
            return False
        else:
            #print("Register sent")
            return True

    def get_data_register(self):

        if self.exec_() == QDialog.Accepted:
            if self._check_if_full():
                user_dict = {}
                userList.append(self.company_name_val.text())
                userList.append(self.user_name_val.text())
                userList.append(self.user_surname_val.text())
                userList.append(self.email_val.text())
                userList.append(self.user_val.text())
                userList.append(self.pass_val.text())
                userList.append(self.current_version_val.text())
                for i in range(len(self.form_dict)):
                    user_dict[self.form_dict[i]] = userList[i]
                pp = pprint.PrettyPrinter()
                pp.pprint(user_dict)
                return user_dict



if __name__ == '__main__':
    import sys
    app = QApplication([])
    access_control = AccessControl()
    access_control.access_request()
    access_control.user_register()

    sys.exit(app.exec_())