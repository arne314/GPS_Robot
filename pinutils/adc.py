import mcp3008

converter = mcp3008.MCP3008()

pins = {
    0: mcp3008.CH0,
    1: mcp3008.CH1,
    2: mcp3008.CH2,
    3: mcp3008.CH3,
    4: mcp3008.CH4,
    5: mcp3008.CH5,
    6: mcp3008.CH6,
    7: mcp3008.CH7,
}


def read_adc(pin):
    return converter.read([pins[pin]])
