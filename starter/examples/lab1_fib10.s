	.text
	.global	_main
	.align	4

_main:
	.cfi_startproc
	stp	X29, X30, [SP, #-16]!
	sub	SP, SP, #128
	mov	X2, #0
	str	X2, [SP, #0]
	ldr	X2, [SP, #0]
	str	X2, [SP, #8]
	mov	X2, #0
	str	X2, [SP, #16]
	ldr	X2, [SP, #16]
	str	X2, [SP, #24]
	mov	X2, #0
	str	X2, [SP, #32]
	ldr	X2, [SP, #32]
	str	X2, [SP, #40]
	mov	X2, #1
	str	X2, [SP, #48]
	ldr	X2, [SP, #48]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #56]
	ldr	X2, [SP, #56]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #64]
	ldr	X2, [SP, #64]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #72]
	ldr	X2, [SP, #72]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #80]
	ldr	X2, [SP, #80]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #88]
	ldr	X2, [SP, #88]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #96]
	ldr	X2, [SP, #96]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #104]
	ldr	X2, [SP, #104]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	ldr	X0, [SP, #8]
	ldr	X1, [SP, #24]
	add	X2, X0, X1
	str	X2, [SP, #112]
	ldr	X2, [SP, #112]
	str	X2, [SP, #40]
	ldr	X2, [SP, #24]
	str	X2, [SP, #8]
	ldr	X2, [SP, #40]
	str	X2, [SP, #24]
	ldr	X2, [SP, #8]
	stp	X29, X30, [SP, #-16]!
	str	X2, [SP, #-16]!
	adrp	X0, l._dformat@PAGE
	add	X0, X0, l._dformat@PAGEOFF
	bl	_printf
	add	SP, SP, #16
	ldp	X29, X30, [SP], #16
	add	SP, SP, #128
	ldp	X29, X30, [SP], #16
	ret
	.cfi_endproc

	.data
l._dformat:
	.asciz	"%d\n"
