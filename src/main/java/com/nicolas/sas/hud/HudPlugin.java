package com.nicolas.sas.hud;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.command.UnknownCommandEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scoreboard.ScoreboardManager;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextColor;
import io.papermc.paper.scoreboard.numbers.NumberFormat;
import org.bukkit.scoreboard.Criteria;
import org.bukkit.scoreboard.DisplaySlot;
import org.bukkit.scoreboard.Objective;
import org.bukkit.scoreboard.Scoreboard;
import java.lang.reflect.Method;
import java.util.UUID;

public final class HudPlugin extends JavaPlugin implements Listener {
    @Override public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getServer().getScheduler().runTaskTimer(this, () ->
                Bukkit.getOnlinePlayers().forEach(this::show), 20L, 40L);
    }
    @EventHandler public void join(PlayerJoinEvent event) { show(event.getPlayer()); }
    @EventHandler public void unknown(UnknownCommandEvent event) {
        if (event.getSender() instanceof Player player) {
            event.message(Component.empty());
            player.sendActionBar(Component.text("Comando inexistente. ", TextColor.color(255, 85, 85))
                    .append(Component.text("Use /comandos.", TextColor.color(245, 245, 245))));
        }
    }
    private void show(Player player) {
        ScoreboardManager manager = Bukkit.getScoreboardManager();
        if (manager == null) return;
        if (!isAuthenticated(player)) {
            player.setScoreboard(manager.getNewScoreboard());
            return;
        }
        Scoreboard scoreboard = manager.getNewScoreboard();
        Objective objective = scoreboard.registerNewObjective("real_status", Criteria.DUMMY, Component.text(" "));
        objective.numberFormat(NumberFormat.blank());
        objective.setDisplaySlot(DisplaySlot.SIDEBAR);
        org.bukkit.scoreboard.Team team = scoreboard.registerNewTeam("status_0");
        team.addEntry("§0");
        team.prefix(Component.text(isBedrock(player)
                ? "sas.opik.net:19132" : "sas.opik.net:25565",
                TextColor.color(82, 251, 83)));
        objective.getScore("§0").setScore(1);
        player.setScoreboard(scoreboard);
    }

    private boolean isAuthenticated(Player player) {
        try {
            org.bukkit.plugin.Plugin account = Bukkit.getPluginManager().getPlugin("SaS_Account");
            if (account == null) return false;
            Method method = account.getClass().getMethod("isPlayerAuthenticated", Player.class);
            return (boolean) method.invoke(account, player);
        } catch (ReflectiveOperationException ignored) {
            return false;
        }
    }

    private boolean isBedrock(Player player) {
        try {
            Class<?> api = Class.forName("org.geysermc.floodgate.api.FloodgateApi");
            Object instance = api.getMethod("getInstance").invoke(null);
            Method method = api.getMethod("isFloodgatePlayer", UUID.class);
            return (boolean) method.invoke(instance, player.getUniqueId());
        } catch (ReflectiveOperationException | LinkageError ignored) {
            return false;
        }
    }
}
