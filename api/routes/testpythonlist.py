try:
    raise Exception("Image improvement failde", "L'amélioration du document a échoué", "test")
except Exception as e:
    print(e.args[1])