package com.example;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class App {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/UNIVERSITY_DB";
        String userName = "root";
        String password = "xodud76005041!K";

        try (Connection connection = DriverManager.getConnection(url, userName, password);
             Statement statement = connection.createStatement();
             ResultSet resultSet = statement.executeQuery("SELECT * FROM student")) {

            int count = 0;
            while (resultSet.next() && count < 3) {
                String name = resultSet.getString("name");  // 실제 컬럼명으로 수정 필요
                System.out.println(name);
                count++;
            }

        } catch (SQLException e) {
            System.err.println(" 오류 발생");
            System.err.println("SQLState : " + e.getSQLState());
            System.err.println("ErrorCode: " + e.getErrorCode());
            System.err.println("Message  : " + e.getMessage());
            e.printStackTrace();
        }
    }
}
