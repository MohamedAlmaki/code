from datetime import date, timedelta
import pytest
from model import Batch, OrderLine, allocate

# from model import ...

today = date.today()


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("1", "SMALL_TABLE", qty=20, eta=today)
    line = OrderLine("1", "SMALL_TABLE", 2)

    batch.allocate(line)
    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("SMALL_TABLE", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("SMALL_TABLE", 2, 3)
    assert not small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    equal_batch, equal_line = make_batch_and_line("SMALL_TABLE", 2, 2)
    assert equal_batch.can_allocate(equal_line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert not batch.can_allocate(different_sku_line)


def test_deallocate():
    batch, line = make_batch_and_line("EXPENSIVE-FOOTSTOOL", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    batch, deallocated_line = make_batch_and_line("SMALL_TABLE", 20, 2)
    batch.deallocate(deallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR_DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
