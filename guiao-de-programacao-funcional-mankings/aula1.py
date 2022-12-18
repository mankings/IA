#Exercicio 1.1
def comprimento(lista):
	if lista == []: return 0
	return 1 + comprimento(lista[1:])

#Exercicio 1.2
def soma(lista):
	if lista == []: return 0
	return lista[0] + soma(lista[1:])

#Exercicio 1.3
def existe(lista, elem):
	if lista == []: return False
	if lista[0] == elem: return True
	return existe(lista[1:], elem)

#Exercicio 1.4
def concat(l1, l2):
	if l1 == []: return l2
	if l2 == []: return l1
	lista = l1
	lista[comprimento(lista):] = [l2[0]]
	lista = concat(lista, l2[1:])
	return lista

#Exercicio 1.5
def inverte(lista):
	if lista == []: return []
	inv = inverte(lista[1:])
	inv[comprimento(inv):] = [lista[0]]
	return inv

#Exercicio 1.6
def capicua(lista):
	if lista == []: return True
	if lista[0] == lista[-1]: return capicua(lista[1:-1])
	return False

#Exercicio 1.7
def concat_listas(lista):
	if lista == []: return []
	if comprimento(lista) == 1: return lista[0]
	l1 = lista[0]
	l2 = lista[1]
	lista[1] = concat(l1, l2)
	return concat_listas(lista[1:])

#Exercicio 1.8
def substitui(lista, original, novo):
	if lista == []: return []
	if lista[0] == original: lista[0] = novo
	lista[1:] = substitui(lista[1:], original, novo)
	return lista

#Exercicio 1.9
def fusao_ordenada(lista1, lista2):
	if lista1 == []: return lista2
	if lista2 == []: return lista1
	lista = []
	if lista1[0] < lista2[0]:
		lista = lista + [lista1[0]]
		lista[1:] = fusao_ordenada(lista1[1:], lista2)
	else:
		lista = lista + [lista2[0]]
		lista[1:] = fusao_ordenada(lista1, lista2[1:])
	return lista

#Exercicio 1.10
def lista_subconjuntos(lista):
	pass

#Exercicio 2.1
def separar(lista):
	if not lista:
		return [], []
	lista1, lista2 = separar(lista[1:])
	return ([lista[0][0]] + lista1, [lista[0][1]] + lista2)

#Exercicio 2.2
def remove_e_conta(lista, elem):
	if lista == []: return ([], 0)
	lst, count = remove_e_conta(lista[1:], elem)
	if lista[0] == elem: 
		return (lst, count + 1)
	else:
		lst = [lista[0]] + lst
		return (lst, count)

#Exercicio 3.1
def cabeca(lista):
	if lista == []: return None
	return lista[0]

#Exercicio 3.2
def cauda(lista):
	if lista == []: return None
	return lista[-1]

#Exercicio 3.3
def juntar(l1, l2):
	if comprimento(l1) != comprimento(l2):
		return None
	if not l1: return []
	pares = juntar(l1[1:], l2[1:])
	return ([(l1[0], l2[0])] + pares)

#Exercicio 3.4
def menor(lista):
	if lista == []: return None
	if comprimento(lista) == 1: return lista[0]
	if lista[0] > lista[1]: 
		return menor(lista[1:])
	return menor([lista[0]] + lista[2:])

#Exercicio 3.6
def maior(lista):
	if lista == []: return None
	if comprimento(lista) == 1: return lista[0]
	if lista[0] < lista[1]: 
		return maior(lista[1:])
	return maior([lista[0]] + lista[2:])

def max_min(lista):
	return (menor(lista), maior(lista))

