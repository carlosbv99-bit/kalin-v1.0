package com.agenda;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * Clase principal que representa la agenda personal
 */
public class Agenda {
    private List<Contacto> contactos;
    private Scanner scanner;
    
    public Agenda() {
        this.contactos = new ArrayList<>();
        this.scanner = new Scanner(System.in);
    }
    
    /**
     * Agrega un nuevo contacto a la agenda
     */
    public void agregarContacto() {
        System.out.println("\n--- AGREGAR NUEVO CONTACTO ---");
        
        System.out.print("Nombre: ");
        String nombre = scanner.nextLine();
        
        System.out.print("Teléfono: ");
        String telefono = scanner.nextLine();
        
        System.out.print("Email: ");
        String email = scanner.nextLine();
        
        Contacto nuevoContacto = new Contacto(nombre, telefono, email);
        contactos.add(nuevoContacto);
        
        System.out.println("¡Contacto agregado exitosamente!");
    }
    
    /**
     * Muestra todos los contactos en la agenda
     */
    public void mostrarContactos() {
        System.out.println("\n--- LISTA DE CONTACTOS ---");
        
        if (contactos.isEmpty()) {
            System.out.println("No hay contactos en la agenda.");
            return;
        }
        
        for (int i = 0; i < contactos.size(); i++) {
            System.out.println("\nContacto #" + (i + 1));
            System.out.println(contactos.get(i));
            System.out.println("------------------------");
        }
    }
    
    /**
     * Busca un contacto por nombre
     */
    public void buscarContacto() {
        System.out.println("\n--- BUSCAR CONTACTO ---");
        System.out.print("Ingrese el nombre a buscar: ");
        String nombreBusqueda = scanner.nextLine();
        
        boolean encontrado = false;
        for (Contacto contacto : contactos) {
            if (contacto.getNombre().toLowerCase().contains(nombreBusqueda.toLowerCase())) {
                System.out.println("\nContacto encontrado:");
                System.out.println(contacto);
                System.out.println("------------------------");
                encontrado = true;
            }
        }
        
        if (!encontrado) {
            System.out.println("No se encontraron contactos con ese nombre.");
        }
    }
    
    /**
     * Elimina un contacto de la agenda
     */
    public void eliminarContacto() {
        System.out.println("\n--- ELIMINAR CONTACTO ---");
        System.out.print("Ingrese el nombre del contacto a eliminar: ");
        String nombreEliminar = scanner.nextLine();
        
        boolean eliminado = false;
        for (int i = 0; i < contactos.size(); i++) {
            if (contactos.get(i).getNombre().toLowerCase().equals(nombreEliminar.toLowerCase())) {
                contactos.remove(i);
                System.out.println("Contacto eliminado exitosamente.");
                eliminado = true;
                break;
            }
        }
        
        if (!eliminado) {
            System.out.println("No se encontró un contacto con ese nombre.");
        }
    }
    
    /**
     * Muestra el menú principal de opciones
     */
    public void mostrarMenu() {
        System.out.println("\n=== AGENDA PERSONAL ===");
        System.out.println("1. Agregar contacto");
        System.out.println("2. Mostrar todos los contactos");
        System.out.println("3. Buscar contacto");
        System.out.println("4. Eliminar contacto");
        System.out.println("5. Salir");
        System.out.print("Seleccione una opción: ");
    }
    
    /**
     * Ejecuta la aplicación de la agenda
     */
    public void ejecutar() {
        int opcion;
        
        do {
            mostrarMenu();
            
            while (!scanner.hasNextInt()) {
                System.out.print("Por favor ingrese un número válido: ");
                scanner.next();
            }
            
            opcion = scanner.nextInt();
            scanner.nextLine(); // Consumir la nueva línea
            
            switch (opcion) {
                case 1:
                    agregarContacto();
                    break;
                case 2:
                    mostrarContactos();
                    break;
                case 3:
                    buscarContacto();
                    break;
                case 4:
                    eliminarContacto();
                    break;
                case 5:
                    System.out.println("¡Gracias por usar la Agenda Personal!");
                    break;
                default:
                    System.out.println("Opción no válida. Por favor intente nuevamente.");
            }
            
        } while (opcion != 5);
        
        scanner.close();
    }
}
