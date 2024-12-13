	.section .rodata
.lprintfmt:
	.string "%ld\n"
	.text
	.globl div
	div:
	pushq %rbp
	movq %rsp, %rbp
	subq $32, %rsp
	movq %rdi, -24(%rbp)
	movq %rsi, -16(%rbp)
	.Ldiv_initial:
	movq $0, -8(%rbp)
	movq -8(%rbp), %r11
	cmpq %r11, -16(%rbp)
	jz .L2
	jmp .L2
	.L2:
	movq -24(%rbp), %rax
	cqto
	idivq -16(%rbp)
	movq %rax, -32(%rbp)
	movq -32(%rbp), %rax
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
	subq $32, %rsp
	.Lmain_initial:
	movq $10, -8(%rbp)
	movq -8(%rbp), %rdi
	movq $0, -16(%rbp)
	movq -16(%rbp), %rsi
	callq div
	movq %rax, -24(%rbp)
	movq -24(%rbp), %r11
	movq %r11, -32(%rbp)
	jmp E_main
	E_main:
	movq %rbp, %rsp
	popq %rbp
	retq
