--
-- Database: `lbtest`
--
CREATE DATABASE IF NOT EXISTS `lbtest` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `lbtest`;

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `test`
--

DROP TABLE IF EXISTS `test`;
CREATE TABLE `test` (
  `id` int NOT NULL,
  `info` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
COMMIT;
