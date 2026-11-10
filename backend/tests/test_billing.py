from app.main import pf_sig
def test_signature_skips_empty_only_when_asked():
    p = [("a", "1"), ("b", ""), ("c", "x y")]
    assert pf_sig(p, True) != pf_sig(p, False) and len(pf_sig(p, True)) == 32
