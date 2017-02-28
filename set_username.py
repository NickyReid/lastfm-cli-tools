class SetUsername:

    @classmethod
    def set_username(cls):
        try:
            username_file = open('defaultuser', 'rw+')
        except IOError:
            username_file = open('defaultuser', 'w+')

        username = username_file.read()

        if len(username) < 1:
            username = raw_input('What is your Last.fm username? ')

        username_file = open('defaultuser', 'w+')
        username_file.write(username)
        username_file.close()
