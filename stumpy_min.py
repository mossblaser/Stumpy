class Memory(object):
	def __init__(self, size)   : self.size, self.memory = size, [0] * size
	def __getitem__(self, a)   : return self.memory[a]
	def __setitem__(self, a, v): self.memory[a] = v
def bset(i, b): return (i & b) == b
def test_cc(s, cc):
	for f in "nzvc": cc = cc.replace(f, "s[%s]"%f)
	for f, r in [("!","not "), ("."," and "), ("+"," or ")]: cc = cc.replace(f, r)
	return bool(eval(cc))
def sign_extend(n, b): return ((-1 if bset(n, 1<<(b-1)) else 0)<<b) | n
pc, n, z, v, c = 7, 8, 9, 10, 11
class Stump(object):
	def __init__(self, memory):
		self.memory = memory
		self._regs, self.cc_en = [0]*(8 + 4), False
	def __getitem__(self, r)    : return sign_extend(self._regs[r], 16) if r != 0 else 0
	def __setitem__(self, r, v) : self._regs[r] = v&0xFFFF if r<=7 or self.cc_en else self._regs[r]
	def geta(self, instr):
		if self.instr_type == 2 or (instr&0b11==0): val,carry = (self[(instr>>5) & 0b111]),0
		else:
			carry = (self[(instr>>5) & 0b111])&0x0001
			val = ((self[(instr>>5) & 0b111])>>1)&0x7FFF
			val |= (([val>>14, carry, self[c]][(instr&0b11) - 1]) << 15)
		self[n],self[z],self[v],self[c] = bset(val,0x8000),val==0,0,carry
		return val
	def getb(self, instr):
		if self.instr_type == 1: return self[(instr>>2) & 0b111]
		else:                    return sign_extend(instr&0b11111, 5)
	def addr(self, i): return sign_extend(self.geta(i) + self.getb(i), 16)
	def add(s, i, cin, inv = False):
		a, b = s.geta(i), (s.getb(i) ^ (-1 * inv))
		val = sign_extend((a + b + cin) & 0xFFFF, 16)
		s[(i>>8)&0b111],s[n],s[z],s[c]=val&0xFFFF,bset(val,0x8000),val==0,(val&0xFFFF)<(a&0xFFFF)
		s[v],s[c]=((a<0)and(b<0)and(val>=0))or((a>=0)and(b>=0)and(val<0)), s[c]^inv
	def step(self):
		instr, self[pc] = self.memory[self[pc]], self[pc]+1
		self.instr_type = 3 if bset(instr, 0xF000) else bset(instr, 0x1000) + 1
		self.cc_en = bset(instr, 0x0800) and not(bset(instr, 0xC000))
		if self.instr_type in (1, 2):
			if   instr&0xE800==0xC800: self.memory[self.addr(instr)] = self[(instr>>8)&0b111]
			elif instr&0xE800==0xC000: self[(instr>>8)&0b111] = self.memory[self.addr(instr)]
			elif instr&0xC000==0x0000: self.add(instr, bset(instr, 0x2000)*self[c])
			elif instr&0xC000==0x4000: self.add(instr, (1+(bset(instr,0x2000)*self[c]))%2, True)
			if instr&0xE000==0x8000: self[(instr>>8) & 0b111] = self.geta(instr) & self.getb(instr)
			elif instr&0xE000==0xA000: self[(instr>>8) & 0b111] = self.geta(instr) | self.getb(instr)
		else:
			conditions = "False|c+z|c|z|v|n|!n.v+n.!v|(!n.v+n.!v)+z".split("|")
			b_cond = (instr & 0x0F00) >> 8
			if test_cc(self, conditions[b_cond >> 1]) == bset(b_cond, 0b1):
				self[pc] = self[pc] + sign_extend(instr&0x00FF, 8)
