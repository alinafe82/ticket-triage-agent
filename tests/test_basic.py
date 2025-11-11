from src.router import Router

def test_router_predict():
    r = Router.bootstrap()
    label, prob = r.predict("Need to reset a password")
    assert isinstance(label, str) and 0.0 <= prob <= 1.0
