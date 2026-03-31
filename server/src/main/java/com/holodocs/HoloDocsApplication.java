package com.holodocs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class HoloDocsApplication {

    public static void main(String[] args) {
        // Virtual threads enabled via application.properties
        SpringApplication.run(HoloDocsApplication.class, args);
    }
}
