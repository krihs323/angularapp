<?php

/////sc_begin_trans();

//Si es inclusion o retiro pueden haber uno o varios benericiarios
//para los  otros casos el valor sera null.
//sc_alert('ddd'.$lc_tpo_nvdd_cdgo);

$ll_ingrso_nvdds = false;

//Verificar si la variable global pn_id_tpo_csa_nvdd_ge llega vacia, si es asi entonces esta es reemplazada por la variable global pn_cdgo_tpo_nvdd que viene desde el formulario de novedades de higia
//Cambia por que ahora el id_tpo_csa_nvdd_ge es seleccionado desde el listado de contratos, ya no es una variable unica como lo era anteriormente.


if (empty([pn_id_tpo_csa_nvdd_ge]))
{
	$lc_tpo_nvdd_cdgo = [pn_cdgo_tpo_nvdd];
	$lc_csa_nvdd_cdgo = '-1'; //-> debe sacarse del ciclo
}
else
{

	// Check for record
	$check_sql = "  select
						a.id,
						c.cdgo,
						e.cdgo as cdgo_csa_nvdd
					from
						[pc_schema].tbtipos_causas_novedades_ge a
					inner join [pc_schema].tbtipos_novedades_ge b on
						a.id_tpo_nvdd_ge = b.id
					inner join [pc_schema].tbtipos_novedades c on
						b.id_tpo_nvdd = c.id
					inner join [pc_schema].tbcausas_novedades_ge d on a.id_csa_nvdd_ge = d.id
					inner join [pc_schema].tbcausas_novedades e on d.id_csa_nvdd = e.id
					where
						a.id = " . [pn_id_tpo_csa_nvdd_ge];
	sc_lookup(rs, $check_sql);
	if (isset({rs[0][0]}))     // Row found
	{
		$lc_tpo_nvdd_cdgo = {rs[0][1]};
		$lc_csa_nvdd_cdgo = {rs[0][2]};
	}else{

		$lc_tpo_nvdd_cdgo = '';
		/////sc_rollback_trans();
		return [false,$check_sql];
	}
}

///error_log("SIIIIII", 3, "../archivos_control/error_log.txt");

if( $lc_tpo_nvdd_cdgo == '5' ||  $lc_tpo_nvdd_cdgo == '6' ||  $lc_tpo_nvdd_cdgo == '9')
	{

		//Se valida que exista un contrato
		if(empty([pn_id_cntrto_bnfcro])){
			/////sc_rollback_trans();
			return [false,$lc_tpo_nvdd_cdgo];
		}

		//como pueden haber varios beneficiarios, fabricamos un INSERT multiple
		$insert_sql_dtlle = "INSERT INTO [pc_schema].tbnovedades_contratos
		(id_cntrto,
		id_cntrto_bnfcro,
		fcha_ocrrnca,
		id_lgn_nvdd_ge,
		id_lgn_crcn_ge,
		id_lgn_mdfccn_ge,
		fcha_crcn,
		fcha_mdfccn,
		jstfccn,
		id_tpo_csa_nvdd_ge,
		id_undd_ngco
		) VALUES ";

		//formamos el IN (id1,id2,...) para UPDATE en tbcontratos_beneficiarios
		$lc_in_id_cntrto_bnfcro = str_replace(';', ',', [pn_id_cntrto_bnfcro]);

		//array con los ids de los contratos_beneficiarios:


		$la_id_cntrto_bnfcro = explode( ';',[pn_id_cntrto_bnfcro] );

		foreach ( $la_id_cntrto_bnfcro as $ln_cntrto_bnfcro )
			{
				$insert_sql_dtlle .= "(".[pn_id_cntrto].",
				".$ln_cntrto_bnfcro.",
				'".[pd_fcha_actvcn]."',
				".[pn_id_lgn_ssn_ge].",
				".[pn_id_lgn_ssn_ge].",
				".[pn_id_lgn_ssn_ge].",
				CURRENT_TIMESTAMP(0),
				CURRENT_TIMESTAMP(0),
				'".[pc_jstfccn]."',
				".[pn_id_tpo_csa_nvdd_ge].",
				".[pn_id_undd_ngco]."),";

			}//Fin del foreach
		$insert_sql_dtlle = substr ( $insert_sql_dtlle , 0, -1 );
		sc_exec_sql($insert_sql_dtlle);


		//Actualizamos tbcontratos_beneficiarios
		if($lc_tpo_nvdd_cdgo == '5')
			{
				//Si es inclusion cambia a activo
				$ln_actlzr_fcha = "fcha_actvcn = '".[pd_fcha_actvcn]."'";
				$ln_id_estdo_rgstro_ge = validar_estados_registros('1');
			}
		elseif($lc_tpo_nvdd_cdgo == '6')
			{
				//Si es retiro cambia a cancelado
				$ln_actlzr_fcha = "fcha_rtro = CURRENT_TIMESTAMP(0)";
				$ln_id_estdo_rgstro_ge = validar_estados_registros('15');


			}
		elseif($lc_tpo_nvdd_cdgo == '9')
			{
				$ln_actlzr_fcha = "fcha_rtro = NULL";
				$ln_id_estdo_rgstro_ge = validar_estados_registros('11');
			}
		//Inlcuision que viene desde Higia GENERACIÓN PRELIMINAR CONTRATO
		/*elseif($lc_tpo_nvdd_cdgo == '19')
			{
				$ln_actlzr_fcha = " fcha_actvcn = fcha_actvcn ";
				$ln_id_estdo_rgstro_ge = validar_estados_registros('1');
			}*/

		$update_sql = "UPDATE [pc_schema].tbcontratos_beneficiarios  "
			."SET ".$ln_actlzr_fcha.", "
			."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge.","
			."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
			."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
			."WHERE id IN (" .$lc_in_id_cntrto_bnfcro. ") ";
		sc_exec_sql($update_sql);

		if ($lc_tpo_nvdd_cdgo == '6'){
			$check_sql_vlr =   "SELECT sum(vlr_bnfcro)as vlr,count(tbcontratos_beneficiarios.id) as ttl
								FROM [pc_schema].tbcontratos_beneficiarios
								INNER JOIN [pc_schema].tbestadosregistros_ge
								ON [pc_schema].tbestadosregistros_ge.id = [pc_schema].tbcontratos_beneficiarios.id_estdo_rgstro_ge
								INNER JOIN [pc_schema].tbestadosregistros
								ON [pc_schema].tbestadosregistros_ge.id_estdo_rgstro = [pc_schema].tbestadosregistros.id
								WHERE
								[pc_schema].tbcontratos_beneficiarios.id_cntrto = ".[pn_id_cntrto]."  AND
								[pc_schema].tbestadosregistros.cdgo in('7','6','1','11','12','13','14')";

				sc_lookup(rs_cntrto_vlr, $check_sql_vlr);
		if(isset({rs_cntrto_vlr[0][0]})){
			$update_sql = "UPDATE [pc_schema].tbcontratos	SET vlr_cntrto = ".{rs_cntrto_vlr[0][0]}." , nmro_bnfcrs = ".{rs_cntrto_vlr[0][1]}."  WHERE id =".[pn_id_cntrto];
			$lc_cmbs_cntrto ="Datos Modificados Del Contrato : Nuevo Valor Contrato : ".{rs_cntrto_vlr[0][0]}." Numero de Beneficiarios : ".{rs_cntrto_vlr[0][1]}."";

		}else{
			$update_sql = "UPDATE [pc_schema].tbcontratos	SET vlr_cntrto = 0 , nmro_bnfcrs = 0 WHERE id =".[pn_id_cntrto];
			$lc_cmbs_cntrto ="Datos Modificados Del Contrato : Nuevo Valor Contrato : 0 Numero de Beneficiarios : 0";				}
			sc_exec_sql($update_sql);
		}


		//En inclusion Actualizar la tbusuarios_empresa_une estado a true
		//Y para el caso de inclusion debe crear una "replica" en ips
		if($lc_tpo_nvdd_cdgo == '5')
		{
			replicar($lc_in_id_cntrto_bnfcro);
		}
		// Y debemos salir de la aplicacion ya sea con un exit o con lo que sea

		/////sc_commit_trans();
		$ll_ingrso_nvdds = true;
	}//fin caso inclusion y retiro
else
	{


		//insert natural que hace scriptcase
		// [pn_id_cntrto_bnfcro] sera null
		//[pn_id_cntrto_bnfcro] = NULL;

		//{id_lgn_nvdd_ge} = [pn_id_lgn_ssn_ge];
		//{id_lgn_crcn_ge}  = [pn_id_lgn_ssn_ge];
		//{id_lgn_mdfccn_ge}  = [pn_id_lgn_ssn_ge];
		//{id_undd_ngco} = [pn_id_undd_ngco];

		//reactivacion 1, suspension 2, cancelacion 3
		$la_cdgo_cntrts = array('1', '2', '3');//casos en que debe salir form grid para elegir contratos


		//si es ANULACION
		//el registro de tbcontratos cambian a e anulado
		if ($lc_tpo_nvdd_cdgo=='4')
			{

				$ln_id_estdo_rgstro_ge_cntrto = validar_estados_registros('5');

				$check_sql = "SELECT [pc_schema].tbcontratos_beneficiarios.id
								FROM [pc_schema].tbcontratos_beneficiarios
							  	INNER JOIN [pc_schema].tbcontratos
								ON [pc_schema].tbcontratos.id = [pc_schema].tbcontratos_beneficiarios.id_cntrto
							 	INNER JOIN [pc_schema].tbplanes_une
								ON [pc_schema].tbcontratos.id_pln_une = [pc_schema].tbplanes_une.id
							  	INNER JOIN [pc_schema].tbplanes
								ON [pc_schema].tbplanes_une.id_pln = [pc_schema].tbplanes.id
							  	WHERE [pc_schema].tbcontratos_beneficiarios.id_cntrto = " . [pn_id_cntrto] . "
								AND  [pc_schema].tbcontratos_beneficiarios.fcha_rtro IS NULL
								AND [pc_schema].tbplanes.cdgo_sprslud IS NOT NULL ";

					sc_select(rs, $check_sql);

					   while(!$rs->EOF)
						{
							$ln_cntrto_bnfcro = $rs->fields[0];
							novedades_bdua_new($ln_cntrto_bnfcro,'N24');
							if ($lc_csa_nvdd_cdgo=='12')
								{
									novedades_bdua_new($ln_cntrto_bnfcro,'N09');
								}
							$rs->MoveNext();
						}
					 	$rs->Close();

				// inserto la novedad de anulacion del contrato

				$insert_sql_dtlle = "INSERT INTO [pc_schema].tbnovedades_contratos
					(id_cntrto,fcha_ocrrnca,id_lgn_nvdd_ge,id_lgn_crcn_ge,
					id_lgn_mdfccn_ge,fcha_crcn,fcha_mdfccn,jstfccn,id_tpo_csa_nvdd_ge,id_undd_ngco)
					VALUES(".[pn_id_cntrto].",now(),".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge]
						.",now(),now(),'".[pc_jstfccn]."',".[pn_id_tpo_csa_nvdd_ge].",".[pn_id_undd_ngco].")";
				sc_exec_sql($insert_sql_dtlle);

				$update_sql = "UPDATE [pc_schema].tbcontratos  "
				."SET "
				."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.", "
				."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
				."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
				."WHERE id  = ".[pn_id_cntrto];
				sc_exec_sql($update_sql);

				// inserto la novedad de anulacion por cada beneficiario del contrato
				$insert_sql_dtlle = "INSERT INTO [pc_schema].tbnovedades_contratos
					(id_cntrto,id_cntrto_bnfcro,fcha_ocrrnca,id_lgn_nvdd_ge,id_lgn_crcn_ge,
					id_lgn_mdfccn_ge,fcha_crcn,fcha_mdfccn,jstfccn,id_tpo_csa_nvdd_ge,id_undd_ngco)
					SELECT id_cntrto,id,now(),".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge]
						.",now(),now(),'".[pc_jstfccn]."',".[pn_id_tpo_csa_nvdd_ge].",".[pn_id_undd_ngco]
					." FROM [pc_schema].tbcontratos_beneficiarios
					WHERE id_cntrto=".[pn_id_cntrto]." AND fcha_rtro IS NULL";
				sc_exec_sql($insert_sql_dtlle);

				//Anulamos beneificiarios pero solo los que fcha_rtro sea = null
				$update_sql = "UPDATE [pc_schema].tbcontratos_beneficiarios  "
				."SET  "
				."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.","
				."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
				."fcha_rtro=CURRENT_TIMESTAMP(0) , "
				."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
				."WHERE id_cntrto = ".[pn_id_cntrto]."
				AND fcha_rtro IS NULL ";
				sc_exec_sql($update_sql);

				// si el usuario es standard (probable zona protegida) se debe actualizar el estado en [pc_schema].tbusuarios_une
				$check_sql = "SELECT b.id_usro_une
					FROM [pc_schema].tbcontratos a inner join
						[pc_schema].tbusuarios_empresas_une b on a.id_usro_emprsa_une=b.id inner join
					  [pc_schema].tbusuarios_une c on b.id_usro_une=c.id
					WHERE a.id =".[pn_id_cntrto]." and c.aplca_usro_stndrd=true";
				sc_lookup(rs, $check_sql);
				if (isset({rs[0][0]}))     // Row found
				{
					$ln_id_usro_une={rs[0][0]};
					$update_table  = [pc_schema].'.tbusuarios_une';      // Table name
					$update_where  = "id = '$ln_id_usro_une'"; // Where clause
					$update_fields = array(   // Field list, add as many as needed
						 "id_estdo_rgstro_ge = '$ln_id_estdo_rgstro_ge_cntrto'",
						 "id_lgn_mdfccn_ge = '[pn_id_lgn_ssn_ge]'",
						 "fcha_mdfccn=now()");

					// Update record
					$update_sql = 'UPDATE ' . $update_table
						. ' SET '   . implode(', ', $update_fields)
						. ' WHERE ' . $update_where;
					sc_exec_sql($update_sql);
				}
			}//fin caso anulacion
		elseif(in_array($lc_tpo_nvdd_cdgo, $la_cdgo_cntrts))
		{
				//HACemos insert multiple con los id_contrtot de la temporal
				//contratos beneficiaros va null


				//Se rearma la cadena con los ids de contratos, ya que el id_cntrto viene en json, ejemplo {"id":6,"seleccionado":true,"jstfccn_cntrto":"22222"}

				$la_id_cntrto = json_decode([pn_id_cntrto]);
				$lc_in_id_cntrto = '';
				foreach($la_id_cntrto as $cntrto){
					$lc_in_id_cntrto = $lc_in_id_cntrto . $cntrto->id . ',';
				}
				$lc_in_id_cntrto = substr($lc_in_id_cntrto, 0, -1);

				if ($lc_tpo_nvdd_cdgo == '3') // Si la novedad es cancelacion
					{
						$check_sql = " SELECT b.id from [pc_schema].tbcontratos_beneficiarios AS b
										INNER JOIN [pc_schema].tbcontratos AS c ON c.id = b.id_cntrto
										INNER JOIN [pc_schema].tbplanes_une AS d ON c.id_pln_une = d.id
										INNER JOIN [pc_schema].tbplanes AS f ON d.id_pln = f.id
										WHERE b.id_cntrto in (".$lc_in_id_cntrto.") and b.fcha_rtro IS NULL AND f.cdgo_sprslud IS NOT null; ";

						sc_select(rs, $check_sql);

					   while(!$rs->EOF)
						{
							$ln_cntrto_bnfcro = $rs->fields[0];
							novedades_bdua_new($ln_cntrto_bnfcro,'N24');
							if ($lc_csa_nvdd_cdgo=='12')
								{
									novedades_bdua_new($ln_cntrto_bnfcro,'N09');
								}
							$rs->MoveNext();
						}
					 	$rs->Close();
					}

				$insert_sql_dtlle = "INSERT INTO [pc_schema].tbnovedades_contratos
				(id_cntrto,
				fcha_ocrrnca,
				id_lgn_nvdd_ge,
				id_lgn_crcn_ge,
				id_lgn_mdfccn_ge,
				fcha_crcn,
				fcha_mdfccn,
				jstfccn,
				id_tpo_csa_nvdd_ge,
				id_undd_ngco
				) VALUES  ";

				foreach($la_id_cntrto as $cntrto_insrt){
					$insert_sql_dtlle = $insert_sql_dtlle . "('".$cntrto_insrt->id."', now(),'".[pn_id_lgn_ssn_ge]."','".[pn_id_lgn_ssn_ge]."','".[pn_id_lgn_ssn_ge]."',now(),now(),'".$cntrto_insrt->jstfccn_cntrto."','".$cntrto_insrt->id_tpo_csa_nvdd_ge."',".[pn_id_undd_ngco]."),";
				}
				$insert_sql_dtlle = substr($insert_sql_dtlle, 0, -1);
				sc_exec_sql($insert_sql_dtlle);

				//Actualizamos los contratos segun sea el caso

				switch ($lc_tpo_nvdd_cdgo)
				{
					case '1':
						$ln_id_estdo_rgstro_ge_cntrto = validar_estados_registros('1');//Pasa a actvos
						break;
					case '2':
						$ln_id_estdo_rgstro_ge_cntrto = validar_estados_registros('11');//pasa a Suspendido
						break;
					case '3':
						$ln_id_estdo_rgstro_ge_cntrto = validar_estados_registros('15');//Pasa a Cancelado
						break;
				}

				$update_sql = "UPDATE [pc_schema].tbcontratos  "
				."SET "
				."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.", "
				."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
				."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
				."WHERE id IN (".$lc_in_id_cntrto.")";
				sc_exec_sql($update_sql);

				// inserto la novedad especificada por cada beneficiario del contrato
				$insert_sql_dtlle = "INSERT INTO [pc_schema].tbnovedades_contratos
					(id_cntrto,id_cntrto_bnfcro,fcha_ocrrnca,id_lgn_nvdd_ge,id_lgn_crcn_ge,
					id_lgn_mdfccn_ge,fcha_crcn,fcha_mdfccn,jstfccn,id_tpo_csa_nvdd_ge,id_undd_ngco) VALUES ";

				foreach($la_id_cntrto as $cntrto_insrt2){
					//Se consultas los beneficiarios de cada contrato seleccionado
					//Realizo un recorrido de sus beneficiarios por cada contrato seleccionado
					$check_sql2 = " SELECT b.id_cntrto, b.id FROM [pc_schema].tbcontratos_beneficiarios b
						WHERE b.id_cntrto = ".$cntrto_insrt2->id." and fcha_rtro IS NULL ";
					sc_select(rs2, $check_sql2);
					while(!$rs2->EOF)
					{
						$insert_sql_dtlle = $insert_sql_dtlle . "('".$rs2->fields[0]."', ".$rs2->fields[1].", now(), ".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge].",".[pn_id_lgn_ssn_ge]
							.",now(),now(), '".$cntrto_insrt2->jstfccn_cntrto."', ".$cntrto_insrt2->id_tpo_csa_nvdd_ge.", ".[pn_id_undd_ngco]." ),";

						$rs2->MoveNext();
					}
					$rs2->Close();
				}
				$insert_sql_dtlle = substr($insert_sql_dtlle, 0, -1);
				sc_exec_sql($insert_sql_dtlle);
				//////return [$insert_sql_dtlle, "ok"];
				//Se debe Suspender  los benefciarios del contratos
				//a excepcion de los que tienen fecha_retiro diferente a null

			if ($lc_tpo_nvdd_cdgo == '3') // Si la novedad es cancelacion
					{
						//estado de los beneficiarios
						$ln_id_estdo_rgstro_bnfcrio = validar_estados_registros('1');//solo beneficiarios activos
						$ln_id_estdo_rgstro_bnfcrio = $ln_id_estdo_rgstro_bnfcrio.','.validar_estados_registros('11');//solo beneficiarios suspendidos

						$update_sql = "UPDATE [pc_schema].tbcontratos_beneficiarios  "
						."SET  "
						."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.","
						."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
						."fcha_rtro= now(), "
						."fcha_mdfccn = now() "
						."WHERE id_cntrto IN (".$lc_in_id_cntrto.")
						AND fcha_rtro IS NULL
						AND id_estdo_rgstro_ge in(".$ln_id_estdo_rgstro_bnfcrio.")";
					}
				elseif($lc_tpo_nvdd_cdgo == '2')
					{

						//estado de los beneficiarios
						$ln_id_estdo_rgstro_bnfcrio = validar_estados_registros('1');//solo beneficiarios activos

						$update_sql = "UPDATE [pc_schema].tbcontratos_beneficiarios  "
						."SET  "
						."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.","
						."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
						."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
						."WHERE id_cntrto IN (".$lc_in_id_cntrto.")
						AND fcha_rtro IS NULL
						AND id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_bnfcrio."";
					}
				elseif($lc_tpo_nvdd_cdgo == '1')
					{

						//estado de los beneficiarios
						$ln_id_estdo_rgstro_bnfcrio = validar_estados_registros('11');//solo beneficiarios suspendidos
            $ln_id_estdo_rgstro_bnfcrio_rtrdo = validar_estados_registros('50');//solo beneficiarios DESVINCULADOS

						$update_sql = "UPDATE [pc_schema].tbcontratos_beneficiarios  "
						."SET  "
						."id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.","
						."id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."', "
						."fcha_mdfccn = CURRENT_TIMESTAMP(0)  "
						."WHERE id_cntrto IN (".$lc_in_id_cntrto.")
						AND fcha_rtro IS NULL
						AND id_estdo_rgstro_ge in (".$ln_id_estdo_rgstro_bnfcrio.", ".$ln_id_estdo_rgstro_bnfcrio_rtrdo.")  ";
					}
				sc_exec_sql($update_sql);
				// si el usuario es standard (probable zona protegida) se debe actualizar el estado en [pc_schema].tbusuarios_une

				$update_sql = "UPDATE [pc_schema].tbusuarios_une
					SET  id_estdo_rgstro_ge = ".$ln_id_estdo_rgstro_ge_cntrto.",
						id_lgn_mdfccn_ge = '".[pn_id_lgn_ssn_ge]."',
						fcha_mdfccn = CURRENT_TIMESTAMP(0)
					WHERE id IN (SELECT c.id_usro_une
					FROM [pc_schema].tbcontratos b inner join
						[pc_schema].tbusuarios_empresas_une c on b.id_usro_emprsa_une=c.id inner join
					    [pc_schema].tbusuarios_une d on c.id_usro_une=d.id
					WHERE b.id in (".$lc_in_id_cntrto.") and d.aplca_usro_stndrd=true)";
		}//fin que elige contratos de form_grid
		/////sc_commit_trans();
		$ll_ingrso_nvdds = true;
	}

	return [$ll_ingrso_nvdds,"ok"];
