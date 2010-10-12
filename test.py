#!/usr/bin/python

import sys

from stumpy import sign_extend
from stumpy import Memory as Memory_
from stumpy import Stump  as Stump_

# Memory wrapper which prints on write
class Memory(Memory_):
	debug  = False
	rdebug = False
	def __setitem__(self, a, v):
		if self.debug:
			print "     memory[%04d] = %04x"%(a,v&0xFFFF)
		Memory_.__setitem__(self, a, v)
	
	def __getitem__(self, a):
		val = Memory_.__getitem__(self, a)
		if self.rdebug:
			print "     memory[%04d]== %04x"%(a,val&0xFFFF)
		return val

# Stump wrapper which has a printable register bank
class Stump(Stump_):
	
	def __str__(self):
		return ("R0 0000 R1 %04x R2 %04x R3 %04x R4 %04x R5 %04x R6 %04x PC %04x "
		       + "CC=%d%d%d%d")%tuple(self._regs[1:])
	
	__repr__ = __str__

def ins_str(instr):
	s = "%16s : "%("0"*16 + bin(instr)[2:])[-16:]
	s += {
		0b000: "add",
		0b001: "adc",
		0b010: "sub",
		0b011: "sbc",
		0b100: "and",
		0b101: "or",
		0b110: "",
		0b111: "b",
	}[instr >> 13]
	
	if instr >> 13 == 0b111:
		s += {
			0b0000: "al",
			0b0001: "nv",
			0b0010: "hi",
			0b0011: "ls",
			0b0100: "cc",
			0b0101: "cs",
			0b0110: "ne",
			0b0111: "eq",
			0b1000: "vc",
			0b1001: "vs",
			0b1010: "pl",
			0b1011: "mi",
			0b1100: "ge",
			0b1101: "lt",
			0b1110: "gt",
			0b1111: "le",
		}[(instr >> 8) & 0xF]
		
		s += " 0x%x"%(sign_extend(instr&0xFF, 8))
		return s
	
	elif instr >> 13 == 0b110:
		if instr >> 11 & 0b1:
			s += "st "
		else:
			s += "ld "
		
		s += "r%d, ["%((instr>>8) & 0b111)
	elif (instr >> 11) & 0b1:
		s += "s "
		s += "r%d, "%((instr >> 8) & 0b111)
	else:
		s += " "
		s += "r%d, "%((instr >> 8) & 0b111)
	
	s += "r%d, "%((instr >> 5) & 0b111)
	
	if (instr >> 12) & 0b1:
		s += "#%d"%(sign_extend(instr&0b11111, 5))
	else:
		s += "r%d"%((instr>>2)&0b111)
		
		s += {
			0b00 : "",
			0b01 : ", asr",
			0b10 : ", ror",
			0b11 : ", rrc"
		}[instr & 0b11]
	
	
	if instr >> 13 == 0b110:
		s += "]"
	
	return s




# Instanciate the emulator
memory = Memory(1<<16)
stump = Stump(memory)

# Load the program into RAM
for addr, line in enumerate(open(sys.argv[1]).read().split("\n")):
	try: memory[addr] = int(line, 2)
	except ValueError: pass


# Time
t = 0

print "     %s"%(stump)
while True:
	raw_input()
	
	print "%03d: memory[%04x]== %s"%(t, stump[7], ins_str(memory[stump[7]]))
	
	memory.rdebug = True
	memory.debug = True
	stump.step()
	memory.rdebug = False
	memory.debug = False
	t+=1
	print "     %s"%(stump)
