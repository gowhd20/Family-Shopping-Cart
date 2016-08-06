
import config
import server

app = server.create_app(config)
app.run()

