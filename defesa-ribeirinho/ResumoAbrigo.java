import java.util.List;
import java.util.Locale;

class ResumoAbrigo {
    record Familia(int pessoas, boolean confirmouAviso, boolean estaNoAbrigo) {}

    public static void main(String[] args) {
        int capacidade = 10;
        var familiasAvisadas = List.of(
            new Familia(4, true, true),
            new Familia(2, true, false),
            new Familia(3, false, false)
        );

        int confirmacoes = 0;
        int pessoasAcolhidas = 0;
        for (Familia familia : familiasAvisadas) {
            if (familia.confirmouAviso()) {
                confirmacoes++;
            }
            if (familia.estaNoAbrigo()) {
                pessoasAcolhidas += familia.pessoas();
            }
        }

        var brasil = Locale.forLanguageTag("pt-BR");
        System.out.printf(brasil, "Aviso confirmado por %d de %d famílias (%.1f%%)%n",
            confirmacoes, familiasAvisadas.size(), 100.0 * confirmacoes / familiasAvisadas.size());
        System.out.printf(brasil, "Abrigo com %d de %d vagas ocupadas (%.1f%%)%n",
            pessoasAcolhidas, capacidade, 100.0 * pessoasAcolhidas / capacidade);
        System.out.println("Vagas disponíveis: " + (capacidade - pessoasAcolhidas));
    }
}
