package com.agenda;

/**
 * Clase principal para ejecutar la aplicación de agenda personal
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("¡Bienvenido a tu Agenda Personal!");
        
        Agenda agenda = new Agenda();
        agenda.ejecutar();
    }
}
