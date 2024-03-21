from website import create_app, socketio
#problem: need socketio from events right away here...which means
#socketio needs to be built first so events need to be made first.
#however, events needs access to db so db needs to be made first
#but db is only made AFTER create app is run.  So socketio in
#event can't have any db dependency... which it needs!!!
#furthermore, can't even pass on the dependency to another file and
#import.  Tried that trick but it doesn't work.

#Then how can we give events db dependency?

app = create_app()

if __name__== '__main__':
    socketio.run(app, debug=True)
