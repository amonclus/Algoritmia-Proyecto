#include "BondPercolation.h"
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <cmath>
#include <chrono>

/**
 * Constructor que inicializa la clase con el número de nodos.
 * Inicializa current_q en 0 para comenzar desde la percolación mínima.
 */
BondPercolation::BondPercolation(int numNodos) : uf(numNodos), uf_aux(numNodos + 2), numNodos(numNodos), current_q(0.0) {
    // Los supernodos se colocan en las posiciones numNodos y numNodos + 1 en la estructura auxiliar
    superTop = numNodos;
    superBottom = numNodos + 1;
}

/**
 * Inicializa los supernodos conectando los nodos del top y bottom en la estructura auxiliar.
 */
void BondPercolation::initialize_supernodes() {
    int grid_size = sqrt(numNodos);  // Tamaño de la grilla
    // Conectar el superTop a los nodos del top y el superBottom a los nodos del bottom
    for (int i = 0; i < grid_size; ++i) {
        uf_aux.unite(superTop, i);  // Conectar el supertop con los nodos del top
        uf_aux.unite(superBottom, numNodos - grid_size + i);  // Conectar el superbottom con los nodos del bottom
    }
}

/**
 * Genera una configuración de pesos aleatorios para las aristas.
 */
vector<pair<Edge, double>> BondPercolation::generate_configuration(const vector<Edge>& aristas) {
    vector<pair<Edge, double>> configuracion;

    unsigned seed = chrono::system_clock::now().time_since_epoch().count();
    srand(seed);

    for (const auto& arista : aristas) {
        double peso = static_cast<double>(rand()) / RAND_MAX;  // Peso aleatorio entre 0 y 1
        configuracion.push_back({arista, peso});
    }

    return configuracion;
}

/**
 * Realiza una percolación incremental. Solo se procesan las aristas cuyo peso esté entre current_q y el nuevo q.
 */
int BondPercolation::generate_single_percolation(const vector<pair<Edge, double>>& configuracion, double q, int &greatest) {
    if (q < current_q) {
        cerr << "Error: No se puede realizar una percolación con un q menor que el actual." << endl;
        return uf.numComponents(numNodos);  // Devuelve el número actual de componentes si no es válido
    }

    // Solo procesar las aristas cuyo peso esté entre current_q y q
    for (const auto& [arista, peso] : configuracion) {
        if (peso > current_q && peso <= q) {
            uf.unite(arista.first, arista.second);  // Unir si el peso está en el rango correcto

            // Actualizar el tamaño del clúster más grande
            int newGreatest = max(uf.get_size(arista.first), uf.get_size(arista.second));
            greatest = max(greatest, newGreatest);

            uf_aux.unite(arista.first, arista.second);  // Unir en la estructura auxiliar
        }
    }

    // Actualizar el valor actual de q
    current_q = q;

    return uf.numComponents(numNodos);  // Devuelve el número de componentes conexos actual
}

/**
 * Realiza una percolación completa para valores de q entre 0 y 1, y devuelve la relación
 * entre q y el número de componentes conexos.
 */
vector<tuple<double, int, int, double>> BondPercolation::generate_full_percolation(const vector<pair<Edge, double>>& configuracion, double step) {
    vector<tuple<double, int, int, double>> resultados;  // Tupla para q, numComponentes, tamaño del clúster más grande, Nsc (Normalized size of the largest cluster)
    int greatest = 1; // Inicializa el clúster más grande como 1 (mínimo posible)

    initialize_supernodes();

    bool percolation = false;  // Bandera para indicar si se ha producido la percolación

    // Recorremos los valores de q entre 0 y 1 usando el step
    for (double q = 0.0; q <= 1.0 + 1e-10; q += step) {
        int numComponentes = generate_single_percolation(configuracion, q, greatest);

        // Calcular Nsc, que es la fracción de nodos en el clúster más grande
        double Nsc = static_cast<double>(greatest) / numNodos;

        // Almacenar los resultados: q, numComponentes, tamaño del clúster más grande, Nsc
        resultados.push_back({q, numComponentes, greatest, Nsc});

        // Verificar si ya se ha producido la percolación
        if (not percolation and has_percolation()) {
            q_c = q;  // Guardar el valor de q crítico
            percolation = true;
            cout << "Percolación detectada a q = " << q_c << endl;
        }
    }

    return resultados;
}

/**
 * Verifica si se ha producido la percolación, es decir, si existe un camino entre el top y el bottom.
 */
bool BondPercolation::has_percolation() {
    return uf_aux.find(superTop) == uf_aux.find(superBottom);
}
