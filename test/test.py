import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

@cocotb.test()
async def test_counter(dut):
    # Set up a 10ns clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0  # uio_in[1] (OE) = 0, uio_in[0] (Load) = 0

    # Reset the DUT
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    # Test 1: Verify output is 0 when Output Enable is low
    assert dut.uo_out.value == 0, f"Expected output 0 when OE is low, got {dut.uo_out.value}"

    # Test 2: Assert Output Enable and check the post-reset value
    await FallingEdge(dut.clk)
    dut.uio_in.value = 2  # Binary 10: uio_in[1] = 1, uio_in[0] = 0
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 1, f"Expected output 1 after reset, got {dut.uo_out.value}"

    # Test 3: Verify counting behavior
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 2, f"Expected count 2, got {dut.uo_out.value}"

    # Test 4: Verify load behavior
    await FallingEdge(dut.clk)
    dut.ui_in.value = 150
    dut.uio_in.value = 3  # Binary 11: uio_in[1] (OE) = 1, uio_in[0] (Load) = 1
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 150, f"Expected loaded value 150, got {dut.uo_out.value}"

    # Test 5: Verify counting resumes from the loaded value
    await FallingEdge(dut.clk)
    dut.uio_in.value = 2  # Binary 10: turn off Load, keep OE on
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 151, f"Expected count 151, got {dut.uo_out.value}"
