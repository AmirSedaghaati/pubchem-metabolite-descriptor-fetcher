# visualize_properties.R
#
# Context: After fetch_pubchem_properties.py retrieves the physicochemical data,
# this script produces two plots that were used in the thesis to justify compound
# selection based on Lipinski's Rule of Five criteria and TPSA thresholds for
# oral bioavailability. The figures were exported as publication-ready PDFs.
#
# The script expects the output CSV produced by the Python fetcher.

library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)

# --- Paths -------------------------------------------------------------------

INPUT_FILE  <- "results/compound_properties.csv"
OUTPUT_DIR  <- "results/"

# -----------------------------------------------------------------------------

df <- read_csv(INPUT_FILE, show_col_types = FALSE)

# Keep only successfully retrieved compounds
df_ok <- df %>% filter(fetch_status == "ok")

if (nrow(df_ok) == 0) {
  stop("No successfully fetched compounds found in '", INPUT_FILE, "'. Run the Python fetcher first.")
}

# Coerce property columns to numeric (PubChem returns them as strings occasionally)
numeric_cols <- c("MolecularWeight", "XLogP", "HBondDonorCount", "HBondAcceptorCount", "TPSA")
df_ok <- df_ok %>%
  mutate(across(all_of(numeric_cols), as.numeric))


# --- Plot 1: Lipinski property overview (scatter: MW vs LogP) ----------------
#
# Lipinski's Rule of Five thresholds are shown as reference lines.
# Compounds outside both thresholds may have reduced oral bioavailability.

p1 <- ggplot(df_ok, aes(x = MolecularWeight, y = XLogP, label = compound_name)) +
  geom_point(aes(color = expected_activity), size = 3.5, alpha = 0.85) +
  geom_text(vjust = -0.8, hjust = 0.5, size = 2.8, color = "grey30") +
  # Lipinski limits
  geom_vline(xintercept = 500, linetype = "dashed", color = "grey50", linewidth = 0.5) +
  geom_hline(yintercept = 5,   linetype = "dashed", color = "grey50", linewidth = 0.5) +
  annotate("text", x = 505, y = min(df_ok$XLogP, na.rm = TRUE),
           label = "MW = 500 Da", hjust = 0, size = 2.5, color = "grey50") +
  annotate("text", x = min(df_ok$MolecularWeight, na.rm = TRUE), y = 5.15,
           label = "LogP = 5", hjust = 0, size = 2.5, color = "grey50") +
  scale_color_brewer(palette = "Set2", name = "Expected activity") +
  labs(
    title    = "Molecular weight vs. lipophilicity (XLogP)",
    subtitle = "Dashed lines: Lipinski Rule of Five thresholds",
    x        = "Molecular weight (Da)",
    y        = "XLogP"
  ) +
  theme_classic(base_size = 11) +
  theme(
    plot.title    = element_text(face = "bold", size = 12),
    plot.subtitle = element_text(color = "grey40", size = 9),
    legend.position = "bottom"
  )

ggsave(
  filename = file.path(OUTPUT_DIR, "lipinski_scatter.pdf"),
  plot     = p1,
  width    = 7, height = 5, units = "in"
)
message("Saved: lipinski_scatter.pdf")


# --- Plot 2: TPSA bar chart --------------------------------------------------
#
# TPSA < 140 Å² is a common threshold for acceptable passive intestinal
# absorption. This chart provides a quick visual check for the full library.

p2 <- ggplot(df_ok, aes(x = reorder(compound_name, TPSA), y = TPSA, fill = expected_activity)) +
  geom_col(width = 0.65, alpha = 0.9) +
  geom_hline(yintercept = 140, linetype = "dashed", color = "firebrick", linewidth = 0.6) +
  annotate("text", x = 0.6, y = 144, label = "TPSA = 140 Å²",
           hjust = 0, size = 2.8, color = "firebrick") +
  scale_fill_brewer(palette = "Set2", name = "Expected activity") +
  coord_flip() +
  labs(
    title = "Topological polar surface area (TPSA) per compound",
    x     = NULL,
    y     = "TPSA (Å²)"
  ) +
  theme_classic(base_size = 11) +
  theme(
    plot.title    = element_text(face = "bold", size = 12),
    legend.position = "bottom"
  )

ggsave(
  filename = file.path(OUTPUT_DIR, "tpsa_barplot.pdf"),
  plot     = p2,
  width    = 7, height = 4.5, units = "in"
)
message("Saved: tpsa_barplot.pdf")
