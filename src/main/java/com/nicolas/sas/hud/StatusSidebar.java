package com.nicolas.sas.hud;

import io.papermc.paper.scoreboard.numbers.NumberFormat;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextColor;
import org.bukkit.scoreboard.Criteria;
import org.bukkit.scoreboard.DisplaySlot;
import org.bukkit.scoreboard.Objective;
import org.bukkit.scoreboard.Scoreboard;
import org.bukkit.scoreboard.ScoreboardManager;
import org.bukkit.scoreboard.Team;

public final class StatusSidebar {
    // Cor-sentinela reconhecida pelos shaders Java para deslocar somente o IP.
    private static final TextColor IP_COLOR = TextColor.color(82, 251, 83);
    private static final String[] ENTRIES = { "§0" };
    private final Scoreboard scoreboard;
    private final Objective objective;
    private final String serverAddress;
    private final Team[] lines = new Team[ENTRIES.length];
    private final boolean[] visible = new boolean[ENTRIES.length];

    public StatusSidebar(ScoreboardManager manager, boolean bedrock) {
        serverAddress = bedrock ? "sas.opik.net:19132" : "sas.opik.net:25565";
        scoreboard = manager.getNewScoreboard();
        objective = scoreboard.registerNewObjective(
                // O Bedrock substitui um título realmente vazio por "?".
                "real_status", Criteria.DUMMY, Component.text(" "));
        objective.numberFormat(NumberFormat.blank());
        objective.setDisplaySlot(DisplaySlot.SIDEBAR);

        for (int index = 0; index < ENTRIES.length; index++) {
            Team team = scoreboard.registerNewTeam("status_" + index);
            team.addEntry(ENTRIES[index]);
            lines[index] = team;
        }
    }

    public Scoreboard scoreboard() {
        return scoreboard;
    }

    public void update() {
        // O placar existe somente para manter o endereço do servidor visível.
        // Vida, fome, armadura, ar e experiência usam novamente o HUD vanilla.
        setLine(0, Component.text(serverAddress, IP_COLOR), true);
    }

    private void setLine(int index, Component content, boolean shouldBeVisible) {
        lines[index].prefix(shouldBeVisible ? content : Component.empty());
        if (visible[index] == shouldBeVisible) {
            return;
        }
        visible[index] = shouldBeVisible;
        if (shouldBeVisible) {
            objective.getScore(ENTRIES[index]).setScore(ENTRIES.length - index);
        } else {
            scoreboard.resetScores(ENTRIES[index]);
        }
    }
}
