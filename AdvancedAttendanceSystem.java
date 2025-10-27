import javax.swing.*;
import javax.swing.border.TitledBorder;
import javax.swing.plaf.nimbus.NimbusLookAndFeel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader; // <-- required
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.time.LocalDate;
import java.util.*;
import java.util.List;

public class AdvancedAttendanceSystem extends JFrame {
    private JTextField studentField, searchField;
    private JTable table;
    private DefaultTableModel model;

    private final Map<String, Map<String, String>> data = new HashMap<>();

    public AdvancedAttendanceSystem() {
        try { UIManager.setLookAndFeel(new NimbusLookAndFeel()); } catch (Exception ignore) {}
        UIManager.put("defaultFont", new Font("SansSerif", Font.PLAIN, 14));

        setTitle("Advanced Attendance Management System");
        setSize(960, 600);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        JPanel content = new JPanel(new BorderLayout(10, 10));
        content.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        content.add(buildTopPanel(), BorderLayout.NORTH);
        content.add(buildCenterPanel(), BorderLayout.CENTER);
        content.add(buildBottomPanel(), BorderLayout.SOUTH);
        add(content, BorderLayout.CENTER);

        setVisible(true);
    }

    private JPanel buildTopPanel() {
        JPanel card = new JPanel(new GridBagLayout());
        card.setBorder(new TitledBorder("Student Management"));
        card.setBackground(Color.white);
        GridBagConstraints gc = new GridBagConstraints();
        gc.insets = new Insets(6, 6, 6, 6);
        gc.gridy = 0; gc.gridx = 0; gc.anchor = GridBagConstraints.WEST;

        JLabel nameLbl = new JLabel("Student:");
        studentField = withPlaceholder(new JTextField(18), "Enter student name");
        JButton addBtn = primaryButton("Add");
        JButton removeBtn = new JButton("Remove");

        JLabel searchLbl = new JLabel("Search:");
        searchField = withPlaceholder(new JTextField(18), "Search by name");
        JButton searchBtn = new JButton("Search");

        addBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { addStudent(); }
        });
        removeBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { removeStudent(); }
        });
        searchBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { applySearch(); }
        });

        gc.gridx = 0; card.add(nameLbl, gc);
        gc.gridx = 1; card.add(studentField, gc);
        gc.gridx = 2; card.add(addBtn, gc);
        gc.gridx = 3; card.add(removeBtn, gc);

        gc.gridy = 1; gc.gridx = 0; card.add(searchLbl, gc);
        gc.gridx = 1; card.add(searchField, gc);
        gc.gridx = 2; card.add(searchBtn, gc);

        return rounded(card);
    }

    private JScrollPane buildCenterPanel() {
        model = new DefaultTableModel(new Object[]{"Student Name", "Last Attendance", "Status"}, 0) {
            @Override public boolean isCellEditable(int row, int column) { return false; }
        };
        table = new JTable(model);
        table.setRowHeight(28);
        table.setFillsViewportHeight(true);

        // Header styling (compact, avoids line-wrap mistakes)
        JTableHeader header = table.getTableHeader();
        Dimension hd = header.getPreferredSize();
        header.setPreferredSize(new Dimension(hd.width, 34));
        header.setFont(header.getFont().deriveFont(Font.BOLD));

        table.setDefaultRenderer(Object.class, new StripedAttendanceRenderer());

        JScrollPane sp = new JScrollPane(table);
        sp.setBorder(new TitledBorder("Attendance Records"));
        return rounded(sp);
    }

    private JPanel buildBottomPanel() {
        JPanel p = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        p.setBorder(new TitledBorder("Actions"));
        p.setBackground(Color.white);

        JButton presentBtn = primaryButton("Mark Present");
        JButton absentBtn = new JButton("Mark Absent");
        JButton saveBtn = new JButton("Save");
        JButton loadBtn = new JButton("Load");

        presentBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { markAttendance("Present"); }
        });
        absentBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { markAttendance("Absent"); }
        });
        saveBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { saveCsv("attendance.csv"); }
        });
        loadBtn.addActionListener(new ActionListener() {
            @Override public void actionPerformed(ActionEvent e) { loadCsv("attendance.csv"); }
        });

        p.add(presentBtn);
        p.add(absentBtn);
        p.add(saveBtn);
        p.add(loadBtn);
        return rounded(p);
    }

    private JButton primaryButton(String text) {
        JButton b = new JButton(text);
        b.setBackground(new Color(33, 150, 243));
        b.setForeground(Color.white);
        b.setFocusPainted(false);
        return b;
    }

    private <T extends JComponent> T rounded(T c) {
        c.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(1, 1, 1, 1, new Color(230, 230, 230)),
                BorderFactory.createEmptyBorder(6, 6, 6, 6)
        ));
        return c;
    }

    private JTextField withPlaceholder(JTextField f, String hint) {
        f.setToolTipText(hint);
        f.setForeground(Color.DARK_GRAY);
        f.addFocusListener(new java.awt.event.FocusAdapter() {
            @Override public void focusGained(java.awt.event.FocusEvent e) { f.repaint(); }
            @Override public void focusLost(java.awt.event.FocusEvent e) { f.repaint(); }
        });
        f.setUI(new javax.swing.plaf.basic.BasicTextFieldUI() {
            @Override protected void paintSafely(Graphics g) {
                super.paintSafely(g);
                if (f.getText().isEmpty() && !f.hasFocus()) {
                    Graphics2D g2 = (Graphics2D) g.create();
                    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
                    g2.setColor(new Color(0, 0, 0, 90));
                    Insets ins = f.getInsets();
                    Font prev = g2.getFont();
                    g2.setFont(f.getFont().deriveFont(Font.ITALIC));
                    g2.drawString(hint, ins.left + 2, f.getHeight() / 2 + f.getFont().getSize() / 2 - 2);
                    g2.setFont(prev);
                    g2.dispose();
                }
            }
        });
        return f;
    }

    private void addStudent() {
        String name = studentField.getText().trim();
        if (name.isEmpty() || data.containsKey(name)) {
            JOptionPane.showMessageDialog(this, "Enter a unique, non-empty name.", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        data.put(name, new HashMap<>());
        model.addRow(new Object[]{name, "-", "-"});
        studentField.setText("");
    }

    private void removeStudent() {
        int r = table.getSelectedRow();
        if (r < 0) {
            JOptionPane.showMessageDialog(this, "Select a student to remove.", "Warning", JOptionPane.WARNING_MESSAGE);
            return;
        }
        String name = (String) model.getValueAt(r, 0);
        data.remove(name);
        model.removeRow(r);
    }

    private void markAttendance(String status) {
        int r = table.getSelectedRow();
        if (r < 0) {
            JOptionPane.showMessageDialog(this, "Select a student to mark attendance.", "Warning", JOptionPane.WARNING_MESSAGE);
            return;
        }
        String name = (String) model.getValueAt(r, 0);
        Map<String, String> record = data.computeIfAbsent(name, k -> new HashMap<>());
        String today = LocalDate.now().toString();
        record.put(today, status);

        model.setValueAt(today, r, 1);
        model.setValueAt(status, r, 2);
    }

    private void applySearch() {
        String q = searchField.getText().trim().toLowerCase();
        refreshTable(q);
    }

    private void refreshTable(String filter) {
        model.setRowCount(0);
        List<String> students = new ArrayList<>(data.keySet());
        Collections.sort(students);
        for (String name : students) {
            if (filter != null && !filter.isEmpty() && !name.toLowerCase().contains(filter)) continue;
            Map<String, String> record = data.getOrDefault(name, Collections.emptyMap());
            String lastDate = latestDate(record.keySet());
            String lastStatus = lastDate.equals("-") ? "-" : record.getOrDefault(lastDate, "-");
            model.addRow(new Object[]{name, lastDate, lastStatus});
        }
    }

    private String latestDate(Set<String> dates) {
        if (dates == null || dates.isEmpty()) return "-";
        String max = null;
        for (String d : dates) {
            if (d == null || d.isEmpty()) continue;
            if (max == null || d.compareTo(max) > 0) max = d;
        }
        return max == null ? "-" : max;
    }

    private void saveCsv(String path) {
        try (PrintWriter pw = new PrintWriter(new FileWriter(path))) {
            pw.println("student,date,status");
            for (Map.Entry<String, Map<String, String>> e : data.entrySet()) {
                String student = escape(e.getKey());
                for (Map.Entry<String, String> rec : e.getValue().entrySet()) {
                    String date = rec.getKey();
                    String status = escape(rec.getValue());
                    if (date != null && !date.isEmpty() && status != null && !status.isEmpty()) {
                        pw.println(student + "," + date + "," + status);
                    }
                }
            }
            JOptionPane.showMessageDialog(this, "Saved to " + path);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error saving: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void loadCsv(String path) {
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            data.clear();
            model.setRowCount(0);
            String line;
            boolean first = true;
            while ((line = br.readLine()) != null) {
                if (first) { first = false; if (line.toLowerCase().startsWith("student,")) continue; }
                String[] parts = line.split(",", -1);
                if (parts.length < 3) continue;
                String student = unescape(parts[0]).trim();
                String date = parts[1].trim();
                String status = unescape(parts[2]).trim();
                if (student.isEmpty() || date.isEmpty() || status.isEmpty()) continue;
                data.computeIfAbsent(student, k -> new HashMap<>()).put(date, status);
            }
            refreshTable("");
            JOptionPane.showMessageDialog(this, "Loaded from " + path);
        } catch (FileNotFoundException nf) {
            JOptionPane.showMessageDialog(this, "File not found: " + path, "Warning", JOptionPane.WARNING_MESSAGE);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private String escape(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }

    private String unescape(String s) {
        s = s == null ? "" : s.trim();
        if (s.startsWith("\"") && s.endsWith("\"") && s.length() >= 2) {
            String body = s.substring(1, s.length() - 1);
            return body.replace("\"\"", "\"");
        }
        return s;
    }

    private static class StripedAttendanceRenderer extends DefaultTableCellRenderer {
        private final Color stripe = new Color(0, 0, 0, 8);
        private final Color present = new Color(198, 239, 206);
        private final Color absent = new Color(255, 199, 206);

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value,
                                                       boolean isSelected, boolean hasFocus,
                                                       int row, int column) {
            Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

            if (isSelected) {
                c.setBackground(table.getSelectionBackground());
                c.setForeground(table.getSelectionForeground());
                return c;
            }

            Color base = table.getBackground();
            if (row % 2 == 0) c.setBackground(base);
            else c.setBackground(new Color(
                    (base.getRed() + stripe.getRed()) / 2,
                    (base.getGreen() + stripe.getGreen()) / 2,
                    (base.getBlue() + stripe.getBlue()) / 2));
            c.setForeground(table.getForeground());

            if (column == 2 && value != null) {
                String v = String.valueOf(value);
                if ("Present".equalsIgnoreCase(v)) c.setBackground(present);
                else if ("Absent".equalsIgnoreCase(v)) c.setBackground(absent);
            }
            return c;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            @Override public void run() { new AdvancedAttendanceSystem(); }
        });
    }
}
