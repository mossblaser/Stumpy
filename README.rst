Stumpy: A Code-Golf, Python STUMP CPU Emulator
==============================================

A small (50 line) STUMP CPU emulator written in Python along with a
quick-and-dirty example "test-bench" program for running STUMP binaries.

The STUMP CPU
-------------
The STUMP is a simple 16-bit RISC microprocessor built as an example during the
VLSI_ course at Manchester University. The specification for this can be found
in the Lab Manual.

.. _VLSI: http://www.cs.manchester.ac.uk/ugt/2010/COMP22111/

The Emulator
------------
The emulator is designed to be consistent with the specification however as it
is *not* a simulator, it is stepped by full fetch-execute-writeback cycles
rather than clock cycles.

Size and Style
``````````````
This project was an enterprise of code golf_ and so the code is not specifically
optimised for speed and simply just for source code size. While the emulator is
correct and accurately emulates all external interfaces, it fits on 50 lines and
just under 100 columns (assuming 2-character tabs). A commented version can be
found in ``stumpy.py`` which is laid out in a semi-readable way (or at least in
the way I developed it) with comments. ``stumpy_min.py`` is the same file but
with all comments and empty lines removed.

I have avoided using "cheats" like using semi-colons to concatenate code onto
one line and using list expansion to place multiple assignments on one line
(though in the latter case I do this where it is appropriate or intuative). Some
areas are spaced very inconsistently and not at all in order to fit within a
reasonable line length.

Finally, yes, ``grep`` this for ``eval`` and you will be disapointed to discover
one. This is used to help compact the representations of branch conditions and
while not strictly legit, it can be considered "safe" as it never executes user
code and most importantly, it *does* work!

Usage
`````
The emulator is just a library and doesn't do anything by itself. To use it:

1. Create a ``Memory`` object (passing the size in 16-bit words, usually 1<<16).
   This memory acts like a list indexable by memory address. Simply load your
   program into the memory.
2. Create a ``Stump`` object passing in the memory you created.
3. To step the CPU one instruction at a time, use the ``step()`` method.
4. Registers 0-7 can be accessed as ``my_stump[r]`` where ``my_stump`` is an
   instance of ``Stump`` and ``r`` is the register number.
4. The condition-codes can be accessed using ``my_stump[x]`` where ``my_stump``
   is an instance of ``Stump`` and ``x`` is a constant ``n``, ``z``, ``v`` or
   ``c`` which are defined in ``stumpy.py``. Note that in order to change these
   you may need to set ``cc_en`` in the stumpy instance to ``True``.
5. Memory is obviously accessible by reading the values in the ``Memory``
   instance you created.

The ``Memory`` class may be modified to allow memory-mapped IO, for example, or
to print debugging information on accesses.

.. _golf: http://en.wikipedia.org/wiki/Code_golf#Perl_golf

The Test Interface/Example Program
----------------------------------
An example usage of the module is provided in the form of ``test.py`` which is a
(very, very carelessly hacked-together) program which takes an augment of a
STUMP "binary" file (which is actually ASCII 0s and 1s separated in to word
blocks on individual lines) which is loaded and then executed by the emulator.

When you start the program, the STUMP's registers are printed and a prompt is
shown. The register values (``R0`` -`` PC``) are all in hexadecimal. The
condition code register, 'CC', is displayed in binary with the bits in-order-
corresponding to ``n`` (sign), ``z`` (zero), ``v`` (overflow), ``c`` (carry).
Initially these will always be zeroed out on start (unlike real hardware which
may be undefined with the exception of the program counter and ``R0`` which is
tied to 0).

At the prompt, the following commands are available:

- [nothing]: Just press enter to step the CPU by one instruction.
- m *addr*: Print out the value in the memory address specified by *addr*. This
  may be any valid Python integer format, e.g. ``123``, ``0xFF``, ``0b1101``.
  The value printed will be in hexedecimal.
- m *addr* = *val*: Set the value at the address given to the specified value,
  again these numbers may be any valid Python integer.
- r *num*: Print out the value in the specified register. Registers may be given
  by number, i.e. 0-7. ``R7`` may be accessed as ``pc``. The 'CC' register's
  bits must be accessed individually by specifying the bit, i.e., ``n`` (sign),
  ``z`` (zero), ``v`` (overflow), ``c`` (carry).
- r *num* = *val*: Set the value of the given register where *num* and *val* are
  formatted as above.
- r: Dump all the registers on to the screen.

Tip: Whitespace is optional in the above arguments, e.g. ``r1=0xFFFF`` is
equivalent to ``r 1 = 0xFFFF``.

Note: And yes, numerical values are just passed straight into an eval with no
sanity checking -- what-cha gonna' do about it, punk?

When the CPU is stepped, the time (in steps) is printed (in binary) followed by
the instruction as loaded from the location indicated by the PC followed by a
disassembly of the instruction.

Memory accesses are printed (where ``memory[addr]== val`` indicates a read and
``memory[addr] = val`` indicates a write. Addresses and values are printed in
hexadecimal. Register accesses are currently *not* printed.

Once the instruction has finished executing the registers are dumped onto the
screen and the prompt is shown again.

Assembler and Example Binaries
------------------------------
An assembler and example binaries for the STUMP can be found on department
computers in ``$COMP22111/sasm`` and ``$COMP22111/Cadence/core/test*.s``
respectively. Unfortunately they are university property and so I cannot
distribute these -- sorry!

Correctness
-----------
I have run it against the supplied test programs which while broad are not
exhaustive and it has passed. While I believe the implementation is correct to
the specification, don't rely on it! If you do notice a bug, please feel free to
submit a fix (please explain the bug, how to reproduce and explain your fix --
this is code-golf code!) or report it (with a suitable example case).
