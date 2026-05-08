package com.agenda;

/**
 * Clase que representa un contacto en la agenda personal
 */
public class Contacto {
    private String nombre;
    private String telefono;
    private String email;
    
    // Constructor
    public Contacto(String nombre, String telefono, String email) {
        this.nombre = nombre;
        this.telefono = telefono;
        this.email = email;
    }
    
    // Getters y Setters
    public String getNombre() {
        return nombre;
    }
    
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }
    
    public String getTelefono() {
        return telefono;
    }
    
    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    @Override
    public String toString() {
        return "Nombre: " + nombre + 
               "\nTeléfono: " + telefono + 
               "\nEmail: " + email;
    }
}
