import falcon


class Schedule:
    def get(self):
        return {'lala': '123'}


api = falcon.API()
api.add_route("/schedule", Schedule())