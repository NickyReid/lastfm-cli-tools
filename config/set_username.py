import os


class SetUsername:

    @classmethod
    def set_username(cls):
        try:
            username_file = open(os.path.dirname(os.path.realpath(__file__)) + '/defaultuser', 'rw+')
        except IOError:
            username_file = open(os.path.dirname(os.path.realpath(__file__)) + '/defaultuser', 'w+')

        username = username_file.read()

        if len(username) < 1:
            username = raw_input('What is your Last.fm username? ')

            username_file = open(os.path.dirname(os.path.realpath(__file__)) + '/defaultuser', 'w+')
            username_file.write(username)
            username_file.close()

        return username
