from model import Batch, OrderLine, allocate, OutOfStock
from datetime import date, timedelta
import pytest


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("02", "RETRO_CLOCK", 100, eta=None)
    shipment_batch = Batch("03", "RETRO_CLOCK", 100, eta=tomorrow)
    line = OrderLine("02", "RETRO_CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    today_batch = Batch("04", "MINIMALIST-SPOON", 100, eta=today)
    tomorrow_batch = Batch("05", "MINIMALIST-SPOON", 100, eta=tomorrow)
    later_batch = Batch("06", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("03", "MINIMALIST-SPOON", 10)

    allocate(line, [today_batch, tomorrow_batch, later_batch])

    assert today_batch.available_quantity == 90
    assert tomorrow_batch.available_quantity == 100
    assert later_batch.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("04", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.ref

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("05", "SMALL_FORK", 10, eta=today)
    line1 = OrderLine("05", "SMALL_FORK", 10)
    line2 = OrderLine("05", "SMALL_FORK", 1)

    allocate(line1, [batch])
    with pytest.raises(OutOfStock, match="SMALL_FORK"): 
        allocate(line2, [batch])

