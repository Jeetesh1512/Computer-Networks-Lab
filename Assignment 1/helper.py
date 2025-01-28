from sympy import Poly, symbols

# Define the variable x
x = symbols('x')

CRCPolynomials = {
    "CRC_1"       : "x+1",
    "CRC_4_ITU"   : "x^4 + x^1 + 1",
    "CRC_5_ITU"   : "x^5 + x^4 + x^2 + 1",
    "CRC_5_USB"   : "x^5 + x^2 + 1",
    "CRC_6_ITU"   : "x^6 + x^1 + 1",
    "CRC_7"       : "x^7 + x^3 + 1",
    "CRC_8_ATM"   : "x^8 + x^2 + x^1 + 1",
    "CRC_8_CCITT" : "x^8 + x^7 + x^3 + x^2 + 1",
    "CRC_8_MAXIM" : "x^8 + x^5 + x^4 + 1",
    "CRC_8"       : "x^8 + x^7 + x^6 + x^4 + x^2 + 1",
    "CRC_8_SAE"   : "x^8 + x^4 + x^3 + x^2 + 1",
    "CRC_10"      : "x^10 + x^9 + x^5 + x^4 + x^1 + 1",
    "CRC_12"      : "x^12 + x^11 + x^3 + x^2 + x + 1",
    "CRC_15_CAN"  : "x^15 + x^14 + x^10 + x^8 + x^7 + x^4 + x^3 + 1",
    "CRC-16"      : "x^16 + x^15 + x^2 + 1" 
}

def convToBinary(key):
    # Get the polynomial expression
    polynomial_expr = CRCPolynomials[key]
    
    # Create a polynomial object
    polynomial = Poly(polynomial_expr, x)
    
    # Get the coefficients of the polynomial
    coeffs = polynomial.all_coeffs()
    
    # Convert coefficients to binary representation
    degree = len(coeffs) - 1
    binary = ''.join('1' if i < len(coeffs) and coeffs[i] != 0 else '0' for i in range(degree, -1, -1))
    
    return binary


