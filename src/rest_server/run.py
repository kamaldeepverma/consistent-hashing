from app import createApp

if __name__ == "__main__":
	app = createApp()
	app.run(host = "0.0.0.0", port = "6003", debug = True)
