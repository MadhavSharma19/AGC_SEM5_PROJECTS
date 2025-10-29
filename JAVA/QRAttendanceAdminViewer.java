import javax.swing.*;
import javax.swing.border.TitledBorder;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import java.awt.*;
import java.io.*;
import java.nio.file.*;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.util.*;
import java.util.List;

public class QRAttendanceAdminViewer extends JFrame {
    private final File dataDir = new File("data");
    private final File qrDir = new File("qr");

    public QRAttendanceAdminViewer() {
        try { UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName()); } catch (Exception ignore) {}
        setTitle("QR Attendance - Admin & Viewer");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(980, 640);
        setLocationRelativeTo(null);

        if (!dataDir.exists()) dataDir.mkdirs();
        if (!qrDir.exists()) qrDir.mkdirs();

        JTabbedPane tabs = new JTabbedPane();
        tabs.add("Admin", new AdminPanel());
        tabs.add("Display Attendance", new ViewPanel());
        setContentPane(tabs);
        setVisible(true);
    }

    // -------- Admin --------
    class AdminPanel extends JPanel {
        private final JComboBox<String> classBox = new JComboBox<>();
        private final JTextField newClassField = new JTextField(12);
        private final JTextField studentField = new JTextField(16);
        private final DefaultTableModel studentsModel =
                new DefaultTableModel(new Object[]{"Class","Student","Passkey","QR File"}, 0) {
                    @Override public boolean isCellEditable(int r,int c){ return false; }
                };

        AdminPanel() {
            setLayout(new BorderLayout(10,10));
            setBorder(BorderFactory.createEmptyBorder(10,10,10,10));

            JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT,10,10));
            top.setBorder(new TitledBorder("Classes"));
            JButton addClassBtn = new JButton("Add Class");
            JButton refreshBtn = new JButton("Refresh");
            top.add(new JLabel("New Class:")); top.add(newClassField); top.add(addClassBtn);
            top.add(new JLabel("Select:")); top.add(classBox); top.add(refreshBtn);

            JPanel mid = new JPanel(new FlowLayout(FlowLayout.LEFT,10,10));
            mid.setBorder(new TitledBorder("Add Student"));
            JButton addStudentBtn = new JButton("Add");
            JButton openQR = new JButton("Open QR Folder");
            mid.add(new JLabel("Student:")); mid.add(studentField); mid.add(addStudentBtn); mid.add(openQR);

            JTable table = new JTable(studentsModel);
            table.setRowHeight(26);
            JTableHeader header = table.getTableHeader();
            header.setPreferredSize(new Dimension(header.getPreferredSize().width, 32));
            header.setFont(header.getFont().deriveFont(Font.BOLD));
            JScrollPane sp = new JScrollPane(table);
            sp.setBorder(new TitledBorder("Students"));

            add(top, BorderLayout.NORTH);
            add(mid, BorderLayout.CENTER);
            add(sp, BorderLayout.SOUTH);

            addClassBtn.addActionListener(e -> addClass());
            addStudentBtn.addActionListener(e -> addStudent());
            openQR.addActionListener(e -> {
                try { Desktop.getDesktop().open(qrDir); } catch (Exception ex) { toast("Open folder: "+ex.getMessage()); }
            });
            refreshBtn.addActionListener(e -> loadStudentsTable());
            loadClasses();
            loadStudentsTable();
        }

        private void addClass() {
            String cls = newClassField.getText().trim();
            if (cls.isEmpty()) { toast("Enter class name"); return; }
            try {
                Path p = dataDir.toPath().resolve("class-"+cls+".txt");
                if (Files.exists(p)) { toast("Class exists"); return; }
                Files.write(p, Arrays.asList("# "+cls));
                loadClasses();
                newClassField.setText("");
                toast("Class added");
            } catch (Exception ex) { toast("Error: "+ex.getMessage()); }
        }

        private void loadClasses() {
            classBox.removeAllItems();
            File[] files = dataDir.listFiles((d,f)->f.startsWith("class-") && f.endsWith(".txt"));
            if (files!=null) Arrays.stream(files).sorted()
                    .forEach(f-> classBox.addItem(f.getName().substring(6, f.getName().length()-4)));
        }

        private void addStudent() {
            String cls = (String) classBox.getSelectedItem();
            String name = studentField.getText().trim();
            if (cls==null || cls.isEmpty()) { toast("Select class"); return; }
            if (name.isEmpty()) { toast("Enter student name"); return; }

            String passkey = generatePasskey(15);
            File studentsCsv = new File(dataDir, "students.csv");
            try (PrintWriter pw = new PrintWriter(new FileWriter(studentsCsv, true))) {
                if (studentsCsv.length()==0) pw.println("class,student,passkey");
                pw.println(csv(cls)+","+csv(name)+","+csv(passkey));
            } catch (Exception ex){ toast("Save error: "+ex.getMessage()); return; }

            // QR filename to be generated by web or another script (same payload JSON)
            String qrFile = new File(qrDir, cls+"_"+name.replaceAll("\\s+","_")+".png").getPath();
            studentField.setText("");
            loadStudentsTable();
            toast("Student added. Generate QR for: "+qrFile);
        }

        private void loadStudentsTable() {
            studentsModel.setRowCount(0);
            Map<String,String[]> rows = readCsv(new File(dataDir,"students.csv"));
            rows.values().forEach(arr -> {
                String cls=arr[0], name=arr[1], key=arr[2];
                String qrPath = new File(qrDir, cls+"_"+name.replaceAll("\\s+","_")+".png").getPath();
                studentsModel.addRow(new Object[]{cls,name,key,qrPath});
            });
        }
    }

    // -------- Viewer --------
    class ViewPanel extends JPanel {
        private final JComboBox<String> classBox = new JComboBox<>();
        private final JTextField dateField = new JTextField(10);
        private final DefaultTableModel viewModel =
                new DefaultTableModel(new Object[]{"Student"}, 0) {
                    @Override public boolean isCellEditable(int r,int c){ return false; }
                };

        ViewPanel() {
            setLayout(new BorderLayout(10,10));
            setBorder(BorderFactory.createEmptyBorder(10,10,10,10));

            JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT,10,10));
            top.setBorder(new TitledBorder("Filter"));
            JButton loadBtn = new JButton("Show Presents");
            JButton openData = new JButton("Open Data Folder");
            top.add(new JLabel("Class:")); top.add(classBox);
            top.add(new JLabel("Date (YYYY-MM-DD):")); top.add(dateField);
            top.add(loadBtn); top.add(openData);

            JTable table = new JTable(viewModel);
            table.setRowHeight(26);
            JTableHeader header = table.getTableHeader();
            header.setPreferredSize(new Dimension(header.getPreferredSize().width, 32));
            header.setFont(header.getFont().deriveFont(Font.BOLD));
            JScrollPane sp = new JScrollPane(table);
            sp.setBorder(new TitledBorder("Present Students"));

            add(top, BorderLayout.NORTH);
            add(sp, BorderLayout.CENTER);

            loadClasses();
            dateField.setText(LocalDate.now().toString());

            loadBtn.addActionListener(e -> loadPresents());
            openData.addActionListener(e -> { try { Desktop.getDesktop().open(dataDir); } catch(Exception ex){ toast("Open: "+ex.getMessage()); }});
        }

        private void loadClasses() {
            classBox.removeAllItems();
            File[] files = dataDir.listFiles((d,f)->f.startsWith("class-") && f.endsWith(".txt"));
            if (files!=null) Arrays.stream(files).sorted()
                    .forEach(f-> classBox.addItem(f.getName().substring(6, f.getName().length()-4)));
        }

        private void loadPresents() {
            viewModel.setRowCount(0);
            String cls = (String) classBox.getSelectedItem();
            String date = dateField.getText().trim();
            if (cls==null || date.isEmpty()) { toast("Select class and date"); return; }
            File csvFile = new File(dataDir, "attendance-"+date+".csv");
            if (!csvFile.exists()) { toast("No file: "+csvFile.getName()); return; }
            Map<String,String[]> rows = readCsv(csvFile);
            rows.values().stream()
                .filter(a->a.length>=4 && a[0].equals(date) && a[1].equals(cls) && "Present".equalsIgnoreCase(a[3]))
                .forEach(a-> viewModel.addRow(new Object[]{a[2]}));
        }
    }

    // -------- Utils --------
    private static String generatePasskey(int len) {
        String letters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
        String digits = "23456789";
        String symbols = "@#%&*+-_=?:";
        String all = letters + digits + symbols;
        SecureRandom r = new SecureRandom();
        StringBuilder sb = new StringBuilder();
        sb.append(letters.charAt(r.nextInt(letters.length())));
        sb.append(digits.charAt(r.nextInt(digits.length())));
        sb.append(symbols.charAt(r.nextInt(symbols.length())));
        while (sb.length()<len) sb.append(all.charAt(r.nextInt(all.length())));
        List<Character> chars = new ArrayList<>();
        for (char c: sb.toString().toCharArray()) chars.add(c);
        Collections.shuffle(chars, r);
        StringBuilder out = new StringBuilder();
        for (char c: chars) out.append(c);
        return out.substring(0, len);
    }

    private static Map<String,String[]> readCsv(File f) {
        Map<String,String[]> map = new LinkedHashMap<>();
        if (!f.exists()) return map;
        try (BufferedReader br = new BufferedReader(new FileReader(f))) {
            String line; boolean header=true; int i=0;
            while ((line=br.readLine())!=null) {
                if (header) { header=false; continue; }
                map.put(String.valueOf(i++), line.split(",", -1));
            }
        } catch (Exception ignored) {}
        return map;
    }

    private static String csv(String s) {
        if (s==null) return "";
        if (s.contains(",") || s.contains("\"")) return "\""+s.replace("\"","\"\"")+"\"";
        return s;
    }

    private static void toast(String msg) { JOptionPane.showMessageDialog(null, msg); }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(QRAttendanceAdminViewer::new);
    }
}
