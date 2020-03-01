from django import forms


class FileActionForm(forms.Form):
    file_id = forms.IntegerField(required=True)

    def form_action(self, file):
        raise NotImplementedError()

    def save(self, file):
        # todo
        self.form_action(file)


class FileResultsForm(FileActionForm):
    def form_action(self, file):
        return 
