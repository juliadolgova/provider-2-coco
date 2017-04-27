CREATE DATABASE  IF NOT EXISTS `tuk` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `tuk`;
-- MySQL dump 10.13  Distrib 5.7.12, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: tuk
-- ------------------------------------------------------
-- Server version	5.5.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `provider`
--

DROP TABLE IF EXISTS `provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provider` (
  `PROVIDER_ID` int(11) NOT NULL AUTO_INCREMENT,
  `MNEMO_COCO` varchar(45) DEFAULT NULL COMMENT 'мнемокод в кокосе',
  `CLASS_NAME` varchar(45) DEFAULT NULL COMMENT 'Имя класса, потомка ProvData',
  `SERVICE_CODE` varchar(45) DEFAULT NULL COMMENT 'Код услуги. Оставлять пустым если в классе не предусмотрен параметр service_code при инициализации',
  `DATE_SOURCE` varchar(45) DEFAULT NULL COMMENT 'Оставлять пустым если дата задолженности есть в файле и у класса есть свойство debt_date.\nЕсли дата в файле отсутствует и у класса есть свойство debt_date, то установить равным одному из значений:\ndate_file_created - будет браться дата создания файла\ndate_file_modified - будет браться дата изменения файла\ndate_now - будет браться текущая дата\nmonth_begin - будет браться первое число текущего месяца\n',
  PRIMARY KEY (`PROVIDER_ID`),
  UNIQUE KEY `MNEMO_COCO_UNIQUE` (`MNEMO_COCO`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provider`
--

LOCK TABLES `provider` WRITE;
/*!40000 ALTER TABLE `provider` DISABLE KEYS */;
INSERT INTO `provider` VALUES (1,'ch_avangard','Avangard','','\r'),(2,'ch_chitaoblgaz','Oblgaz','','\r'),(3,'ch_dom1','Dom','3199','\r'),(4,'ch_dom2','Dom','servid_unkn','\r'),(5,'ch_dom4','Dom','3201','\r'),(6,'ch_dom6','Dom','3202','\r'),(7,'ch_dom7','Dom','3203','\r'),(8,'ch_domremstroy','Domremstroy','','date_file_modified'),(9,'ch_dzhin','','','\r'),(10,'ch_energozhilstroy','','','\r'),(11,'ch_energozhilstroy2','','','\r'),(12,'ch_ingoda','Ingoda','','date_file_modified'),(13,'ch_kenon','','','\r'),(14,'ch_lider','Lider','','\r'),(15,'ch_perspektiva','Perspektiva','','\r'),(16,'ch_region','Region','8373','date_file_modified'),(17,'ch_region1','Region','3493','date_file_modified'),(18,'ch_region2','Region','3521','date_file_modified'),(19,'ch_region4','Region','3523','date_file_modified'),(20,'ch_region5','Region','8094','date_file_modified'),(21,'ch_region6','Region','4601','date_file_modified'),(22,'ch_region7','Region','8372','date_file_modified'),(23,'ch_severniy','Severniy','','\r'),(24,'ch_sluzhbazakazchika','Dom','3207','\r'),(25,'ch_smd','SMD','','\r'),(26,'ch_sparta','','','\r'),(27,'ch_teplovodokanal','Teplovodokanal','','\r'),(28,'ch_tgk14','TGK14','','\r'),(29,'ch_vodokanal','Vodokanal','','\r'),(30,'ch_zabfkr','FondKapRem','','date_file_modified'),(31,'ch_zhilkom','Zhilkom','','\r');
/*!40000 ALTER TABLE `provider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registry`
--

DROP TABLE IF EXISTS `registry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registry` (
  `REGISTRY_ID` int(11) NOT NULL AUTO_INCREMENT,
  `PROVIDER_ID` int(11) DEFAULT NULL,
  `STATUS` int(11) DEFAULT NULL COMMENT '1 - только что создан\n2 - загружается\n3 - загружен\n4 - ошибка при загрузке\n5 - критическое число ошибок обработки записей\n',
  `HASH` varchar(45) DEFAULT NULL,
  `FILENAME` varchar(100) DEFAULT NULL,
  `LAST_IMPORTED_ITEM` int(11) DEFAULT NULL,
  `MAX_DEBT_DATE` datetime DEFAULT NULL,
  `ERROR_COUNT` int(11) DEFAULT NULL COMMENT 'Количество ошибочных записей',
  PRIMARY KEY (`REGISTRY_ID`),
  KEY `FK_PROVIDER_idx` (`PROVIDER_ID`),
  CONSTRAINT `FK_REGISTRY_PROVIDER` FOREIGN KEY (`PROVIDER_ID`) REFERENCES `provider` (`PROVIDER_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `task_delete`
--

DROP TABLE IF EXISTS `task_delete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_delete` (
  `TASK_DELETE_ID` int(11) NOT NULL AUTO_INCREMENT,
  `PROVIDER_ID` int(11) DEFAULT NULL,
  `DELETE_BEFORE` datetime DEFAULT NULL,
  `STATUS` int(11) DEFAULT NULL,
  PRIMARY KEY (`TASK_DELETE_ID`),
  KEY `FK_PROVIDER_idx` (`PROVIDER_ID`),
  CONSTRAINT `FK_TASK_DELETE_PROVIDER` FOREIGN KEY (`PROVIDER_ID`) REFERENCES `provider` (`PROVIDER_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'tuk'
--
/*!50003 DROP FUNCTION IF EXISTS `registry_loading_allowed` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `registry_loading_allowed`(_registry_id int) RETURNS tinyint(1)
BEGIN	
	SET @status_before = (select status from registry where REGISTRY_ID=_registry_id);
    if (@status_before <> 1) or (@status_before is null) then
		return False;
	else
		UPDATE registry set status=2 where REGISTRY_ID=_registry_id;
        return True;
	end if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `task_delete_allowed` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `task_delete_allowed`(_task_delete_id int) RETURNS tinyint(1)
BEGIN	
	SET @status_before = (select status from task_delete where TASK_DELETE_ID=_task_delete_id);
    if (@status_before <> 1) or (@status_before is null) then
		return False;
	else
		UPDATE task_delete set status=2 where TASK_DELETE_ID=_task_delete_id;
        return True;
	end if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CREATE_TASKS_DELETE` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CREATE_TASKS_DELETE`()
begin
	DROP TABLE IF EXISTS tmp_max_dates_registry;
	DROP TABLE IF EXISTS tmp_max_dates_task_delete;

	CREATE TEMPORARY TABLE tmp_max_dates_registry AS
	SELECT 
		registry.PROVIDER_ID, 
		MAX(registry.MAX_DEBT_DATE) AS MAX_DATE, 
		DATE_SUB(DATE(MAX(registry.MAX_DEBT_DATE)), INTERVAL 1 MONTH) AS DELETE_BEFORE
	FROM registry
	WHERE registry.STATUS=3 AND registry.MAX_DEBT_DATE IS NOT NULL
	GROUP BY registry.PROVIDER_ID;

	CREATE TEMPORARY TABLE tmp_max_dates_task_delete AS
	SELECT 
		task_delete.PROVIDER_ID, 
		MAX(task_delete.DELETE_BEFORE) AS DELETE_BEFORE
	FROM task_delete
	WHERE task_delete.DELETE_BEFORE IS NOT NULL
	GROUP BY task_delete.PROVIDER_ID;

	INSERT INTO task_delete(PROVIDER_ID, DELETE_BEFORE, STATUS)
	SELECT tmp_max_dates_registry.PROVIDER_ID, tmp_max_dates_registry.DELETE_BEFORE, 1 AS STATUS 
	FROM tmp_max_dates_registry 
	LEFT JOIN tmp_max_dates_task_delete ON tmp_max_dates_registry.PROVIDER_ID=tmp_max_dates_task_delete.PROVIDER_ID 
	WHERE 
		tmp_max_dates_registry.DELETE_BEFORE>tmp_max_dates_task_delete.DELETE_BEFORE 
		OR tmp_max_dates_task_delete.DELETE_BEFORE IS NULL;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-04-27 10:05:30
