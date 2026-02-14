package com.bajosterr;

import java.io.*;
import java.util.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:3000")
public class BassController {

    @PostMapping("/process")
    public Map<String, Object> processYouTube(@RequestBody Map<String, String> body) throws IOException, InterruptedException {
        String url = body.get("url");

        // Ejecuta el script Python
        ProcessBuilder pb = new ProcessBuilder("python", "src/python/process_bass.py");
        pb.redirectErrorStream(true);
        Process process = pb.start();

        // Envía la URL al script
        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()))) {
            writer.write(url + "\n");
            writer.flush();
        }

        // Captura la salida
        List<String> notas = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Convierte la salida en arreglo
                notas.addAll(Arrays.asList(line.split(",")));
            }
        }

        process.waitFor();

        return Map.of("url", url, "notas", notas);
    }
}
