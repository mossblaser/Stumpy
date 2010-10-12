#!/usr/bin/python
# A bit of light code golf -- a miniturized python simulator for the STUMP
# processor from COMP22111, University of Manchester.
# Written by Jonathan Heathcote, 2010, GPLv2
# Without comments and empty lines this file is 50 lines and <100 cols

class Memory(object):
	def __init__(self, size)   : self.size, self.memory = size, [0] * size
	def __getitem__(self, a)   : return self.memory[a]
	def __setitem__(self, a, v): self.memory[a] = v


# Are the given series of bits set?
def bset(i, b): return (i & b) == b


# Test the condition codes for a given condition in mathsy-format given in the
# spec in order to save space... Takes a Stump object and a condition string and
# returns whether the condition is met
def test_cc(s, cc):
	# Expand the operands
	for f in "nzvc": cc = cc.replace(f, "s[%s]"%f)
	
	# Expand the operators
	for f, r in [("!","not "), ("."," and "), ("+"," or ")]: cc = cc.replace(f, r)
	return bool(eval(cc)) # *Trollface*


# Sign extend a b bit number n
def sign_extend(n, b): return ((-1 if bset(n, 1<<(b-1)) else 0)<<b) | n


# Constants for special register numbers
pc, n, z, v, c = 7, 8, 9, 10, 11


class Stump(object):
	
	def __init__(self, memory):
		self.memory = memory
		self._regs, self.cc_en = [0]*(8 + 4), False # Gen-Purpose Regs + CC regs
	
	
	# General Purpose Register and CC register accessors
	def __getitem__(self, r)    : return sign_extend(self._regs[r], 16) if r != 0 else 0
	def __setitem__(self, r, v) : self._regs[r] = v&0xFFFF if r<=7 or self.cc_en else self._regs[r]
	
	
	def geta(self, instr):
		# If no shift needed, return the value
		if self.instr_type == 2 or (instr&0b11==0): val,carry = (self[(instr>>5) & 0b111]),0
		else:
			# Get the carry bit and shift the value
			carry = (self[(instr>>5) & 0b111])&0x0001
			val = ((self[(instr>>5) & 0b111])>>1)&0x7FFF
			
			# Set the top bit and the carry register
			val |= (([val>>14, carry, self[c]][(instr&0b11) - 1]) << 15)
		
		# Set the other flags
		self[n],self[z],self[v],self[c] = bset(val,0x8000),val==0,0,carry
		
		return val
	
	
	def getb(self, instr):
		if self.instr_type == 1: return self[(instr>>2) & 0b111]
		else:                    return sign_extend(instr&0b11111, 5)
	
	
	# Add operands from instruction and return caller
	def addr(self, i): return sign_extend(self.geta(i) + self.getb(i), 16)
	
	
	# Add operands and write output to register, setting carry bits
	def add(s, i, cin, inv = False):
		# Fetch the operands
		a, b = s.geta(i), (s.getb(i) ^ (-1 * inv))
		
		# Do the addition and truncate the result
		val = sign_extend((a + b + cin) & 0xFFFF, 16)
		
		# Update Sign, Zero and Carry status regs and store the result
		s[(i>>8)&0b111],s[n],s[z],s[c]=val&0xFFFF,bset(val,0x8000),val==0,(val&0xFFFF)<(a&0xFFFF)
		
		# Update Overflow bit (If the two operands have the same sign and the sign
		# changes then an overflow has occurred). Invert the carry out if inv. This
		# is done here to save space on the above line...
		s[v],s[c]=((a<0)and(b<0)and(val>=0))or((a>=0)and(b>=0)and(val<0)), s[c]^inv
	
	
	def step(self):
		# Read the instruction and increment the PC
		instr, self[pc] = self.memory[self[pc]], self[pc]+1
		
		# Get the instruction type
		self.instr_type = 3 if bset(instr, 0xF000) else bset(instr, 0x1000) + 1
		
		# Can only change the condition codes if not a branch/load/store
		self.cc_en = bset(instr, 0x0800) and not(bset(instr, 0xC000))
		
		if self.instr_type in (1, 2):
			# Type 1/2 Instruction
			
			# Store
			if   instr&0xE800==0xC800: self.memory[self.addr(instr)] = self[(instr>>8)&0b111]
			# Load
			elif instr&0xE800==0xC000: self[(instr>>8)&0b111] = self.memory[self.addr(instr)]
			# ADD/ADC
			elif instr&0xC000==0x0000: self.add(instr, bset(instr, 0x2000)*self[c])
			# SUB/SBC
			elif instr&0xC000==0x4000: self.add(instr, (1+(bset(instr,0x2000)*self[c]))%2, True)
			
			# AND
			if instr&0xE000==0x8000: self[(instr>>8) & 0b111] = self.geta(instr) & self.getb(instr)
			# OR
			elif instr&0xE000==0xA000: self[(instr>>8) & 0b111] = self.geta(instr) | self.getb(instr)
			
		else:
			# Type 3 Instruction (Branch)
			
			# A | seperated list of condition codes for every-other condition
			conditions = "False|c+z|c|z|v|n|!n.v+n.!v|(!n.v+n.!v)+z".split("|")
			
			# The condition code in the instruction
			b_cond = (instr & 0x0F00) >> 8
			
			# Branch if the condition is met
			if test_cc(self, conditions[b_cond >> 1]) == bset(b_cond, 0b1):
				# Jump relative
				self[pc] = self[pc] + sign_extend(instr&0x00FF, 8)
