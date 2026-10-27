from generator.generation.rng import make_rng


def test_same_seed_and_stream_give_same_sequence() -> None:
    first = make_rng(42, "customers")
    second = make_rng(42, "customers")
    assert [first.random() for _ in range(5)] == [second.random() for _ in range(5)]


def test_different_streams_give_different_sequences() -> None:
    assert make_rng(42, "customers").random() != make_rng(42, "orders").random()


def test_different_seeds_give_different_sequences() -> None:
    assert make_rng(1, "customers").random() != make_rng(2, "customers").random()


def test_streams_do_not_affect_each_other() -> None:
    customers = make_rng(42, "customers")
    expected = [customers.random() for _ in range(3)]

    orders = make_rng(42, "orders")
    _ = [orders.random() for _ in range(1000)]  # сколько бы ни тянули из другого потока

    customers_again = make_rng(42, "customers")
    assert [customers_again.random() for _ in range(3)] == expected
