	.section .rodata
.lprintfmt:
	.string "%ld\n"
	.globl exception
	.data
	exception: .quad 0
	.text
	.globl div
	div:
	pushq %rbp
	movq %rsp, %rbp
	subq $48, %rsp
	movq %rdi, -32(%rbp)
	movq %rsi, -16(%rbp)
	movq $0, -8(%rbp)
	movq -8(%rbp), %r11
	cmpq %r11, -16(%rbp)
	jz .L0
	jmp .L1
	.L0:
	movq $15581045, -24(%rbp)
	movq -24(%rbp), %r11
	movq %r11, exception(%rip)
	movq -24(%rbp), %rax
	jmp E_div
	jmp .L2
	.L1:
	.L2:
	movq -32(%rbp), %rax
	cqto
	idivq -16(%rbp)
	movq %rax, -40(%rbp)
	movq -40(%rbp), %rax
	jmp E_div
	E_div:
	movq %rbp, %rsp
	popq %rbp
	retq
	.text
	.globl main
	main:
	pushq %rbp
	movq %rsp, %rbp
	subq $48, %rsp
	movq $10, -8(%rbp)
	movq -8(%rbp), %rdi
	movq $0, -16(%rbp)
	movq -16(%rbp), %rsi
	callq div
	movq %rax, -24(%rbp)
	movq $0, -32(%rbp)
	movq exception(%rip), %r11
	cmpq %r11, -32(%rbp)
	jz .L3
	jmp E_main
	.L3:
	movq -24(%rbp), %r11
	movq %r11, -40(%rbp)
	jmp E_main
	E_main:
	movq %rbp, %rsp
	popq %rbp
	retq
