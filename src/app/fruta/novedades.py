'''
    Novedades se encarga de gestionar los datos de los novedades
    @author: edison.bejarano
    @since: 21-03-2018
    @summary: Clase para la gestion de  novedades
'''
from Static.ConnectDB import ConnectDB  # @UnresolvedImport
from Static.Utils import Utils  # @UnresolvedImport
from flask_restful import request, Resource
import requests
#from wtforms import Form, validators, StringField , IntegerField
#from ValidacionSeguridad import ValidacionSeguridad  # @UnresolvedImport
import Static.labels as labels # @UnresolvedImport
#import Static.errors as errors  # @UnresolvedImport
#import Static.opciones_higia as optns  # @UnresolvedImport
#import Static.config_DB as dbConf # @UnresolvedImport
import time,json #,jwt
import Static.config_DB as dbConf  # @UnresolvedImport
import Static.config as conf

#Declaracion de variables globales
Utils = Utils()
pc_cnnctDB = ConnectDB()
pd_fcha_act = time.ctime()


class Novedades(Resource):
    lc_cnctn = ConnectDB()
    def post(self,**kwargs):
        try:
            method = kwargs["page"]
            return getattr(self,method)()
        except Exception as e:
            print(e)

    def listar(self):
        ln_id_scrsl = request.form['id_scrsl']
        strSql = " select "\
                    " 	b.dscrpcn as tpo_prcso_dscrpcn, "\
                    " 	a.id_prcso as id_prcso, "\
                    " 	a.fcha_ocrrnca::text as fcha_ocrrnca, "\
                    " 	a.estdo as estadosregistros, "\
                    " 	a.fcha_crcn::text as fcha_crcn, "\
                    " 	a.jstfccn as jstfccn, "\
                    " 	e.dscrpcn as tpo_nvdd, "\
                    " 	g.dscrpcn as csa_nvdd "\
                    " from "\
                    " 	"+dbConf.DB_SHMA+"tbnovedades a "\
                    " inner join "+dbConf.DB_SHMA+"tbtipos_procesos b on "\
                    " 	a.id_prcso_tpo_une = b.id "\
                    " inner join "+dbConf.DB_SHMA+"tbtipos_causas_novedades_ge as c on "\
                    " 	a.id_tpo_csa_nvdd_ge = c.id "\
                    " inner join "+dbConf.DB_SHMA+"tbtipos_novedades_ge d on "\
                    " 	c.id_tpo_nvdd_ge = d.id "\
                    " inner join "+dbConf.DB_SHMA+"tbtipos_novedades e on "\
                    " 	d.id_tpo_nvdd = e.id "\
                    " inner join "+dbConf.DB_SHMA+"tbcausas_novedades_ge f on "\
                    " 	c.id_csa_nvdd_ge = f.id "\
                    " inner join "+dbConf.DB_SHMA+"tbcausas_novedades g on "\
                    " 	f.id_csa_nvdd = g.id "
        Cursor = pc_cnnctDB.queryFree(strSql)
        if Cursor :
            data = json.loads(json.dumps(Cursor, indent=2))
            return Utils.nice_json(data,200)
        else:
            return Utils.nice_json({labels.lbl_stts_success:labels.INFO_NO_DTS},202)


    '''
        @author: Cristian Botina
        @since: 11-01-2019
        @summary: Metodo que recoge los parametros POST y llama a la funcion que inserta la novedad
        @param **kwargs: recibe
        @return: Retorna un status 200, lo cual son novedaes que se ingresan con exito en la base de datos.
    '''
    def crear(self):
        try:
            ll_aplca_intrgra = request.form['aplca_intrgra'] #REQUERIDO
            ln_id_prcso_tpo_une = request.form['id_prcso_tpo_une'] #REQUERIDDO
            ln_id_tpo_csa_nvdd_ge = request.form['id_tpo_csa_nvdd_ge'] #REQUERIDO
            ln_id_prcso = request.form['id_prcso'] #REQUERIDO
            ln_id_lgn_ssn_ge = request.form['id_lgn_crcn_ge'] #REQUERIDO
            ln_id_undd_ngco = request.form['id_undd_ngco'] #REQUERIDO
            ln_jstfccn = request.form['jstfccn'] #REQUERIDO
            ln_id_grpo_emprsrl = request.form['id_grpo_emprsrl'] #REQUERIDO
            if 'estdo' in request.form:
                ll_estdo = request.form['estdo'] #OPCIONAL
            else:
                ll_estdo = 'true'

            #Cuando esta variable llega definida, quiere decir que viene desde el formulario de novedades general,
            #por ende, debe venir definida con el id_tipo_prcso seleccionado y por lo tanto la variable id_tpo_csa_nvdd_ge va a venir vacia, ya que los tipos causas noedades se definen en un json con
            #multiples contratos o beneficiarios, tabin hace que funcionen los test
            '''
            if 'id_tpo_nvdd_ge' in request.form:
                lc_cdgo_tpo_nvdd = request.form['id_tpo_nvdd_ge'] #OPCIONAL
            else:
                lc_cdgo_tpo_nvdd = None
            '''

            if 'id_cntrto_bnfcro' in request.form:
                ln_id_cntrto_bnfcro = request.form['id_cntrto_bnfcro'] #OPCIONAL
            else:
                ln_id_cntrto_bnfcro = None

            if 'fcha_crcn' in request.form:
                lc_fcha_actl = request.form['fcha_crcn'] #OPCIONAL
            else:
                lc_fcha_actl = None

            ##LLAMADO DE LA NUEVA FUNCION
            return self.crearnovedad(ll_aplca_intrgra, ln_id_prcso_tpo_une, ln_id_tpo_csa_nvdd_ge, ln_id_prcso, ln_id_lgn_ssn_ge, ln_id_undd_ngco, ln_jstfccn, ln_id_grpo_emprsrl, ll_estdo,ln_id_cntrto_bnfcro,lc_fcha_actl)
        except Exception as e:
            print("el error",e)
            ##### ojo, descomentar
            ######return Utils.nice_json({labels.lbl_stts_error:"No se pudo crear la novedad"},400)

    #Aplicamos refactorizacion
    def crear_integra(self,data):
        #Se realiza la solicitud a SSIntegra
        print("\n")
        print("DATOS",data)
        print("\n")
        lc_rsltdo = requests.post(Utils.getUrlNovedadesSSIntegra()+'blank_servicio_novedades/blank_servicio_novedades.php', data=data)
        print("texto:"+lc_rsltdo.text)
        print("\n")
        print("\n")
        #Se comprueba que retorne estatus 200, en relacion a la conexion y respuesta de SSI_INTEGRADO
        if (lc_rsltdo.status_code==200):
            #Uso el try para controlar el error 500 de ssintegra
            try:
                lo_objto = json.loads(lc_rsltdo.text)
                #Se comprueba que la respuesta de ssintegra sea ok
                if(lo_objto["status"]==200):
                    return [True,'Se generó satisfactoriamente']
                else:
                    return [False,'SSIntegra no permitio la generación del contrato, error generado:' + str(lo_objto["status"])]
            except Exception as e:
                return [False,'SSIntegra no permitio la generación del contrato, error del servidor 500']

        else:
            return [False, 'Se generó un error de código ' + str(lc_rsltdo.status_code)]

    def crearnovedadcontrato(self):
        lc_fcha_actl = time.ctime()
        objectValues={}

        #valido que llegue el parametro id_cntrto
        try:
            la_id_cntrto = request.form['id_prcso']
            if len(la_id_cntrto) <=2:
                return Utils.nice_json({labels.lbl_stts_error:"No ha seleccionado ningún contrato"},400)
        except Exception as e:
            return Utils.nice_json({labels.lbl_stts_error:"No ha seleccionado ningún contrato"},400)


        try:
            lo_id_cntrto_bnfcro = request.form['id_cntrto_bnfcro']
        except Exception as e:
            lo_id_cntrto_bnfcro = None

        lo_data_contratos=json.loads(la_id_cntrto)
        lc_cdgo_tpo_nvdd = request.form["id_tpo_nvdd_ge"]
        #Se arma una cadena con los id de los contratos seleccionados

        #####lc_id_cntrts = Utils.getObjetoACadenaIn(lo_data_contratos,"id")

        if lc_cdgo_tpo_nvdd=='2':
            #SUSPENSION DE CONTRATOS
            #la_id_cntrto uso esta variable sin pasarle el load json ya que viene con el formato estandar
            return self.crearnovedad('true', '2', request.form['id_tpo_csa_nvdd_ge'], la_id_cntrto, request.form['id_lgn_ge'], request.form['id_undd_ngco'], request.form['jstfccn'], request.form['id_grpo_emprsrl'], 'true', None, None, lc_cdgo_tpo_nvdd)
        elif lc_cdgo_tpo_nvdd=='3':
            #CANCELACION DE CONTRATOS
            #la_id_cntrto uso esta variable sin pasarle el load json ya que viene con el formato estandar
            return self.crearnovedad('true', '2', request.form['id_tpo_csa_nvdd_ge'], la_id_cntrto, request.form['id_lgn_ge'], request.form['id_undd_ngco'], request.form['jstfccn'], request.form['id_grpo_emprsrl'])
            #RETIRO DE CONTRATO
        elif lc_cdgo_tpo_nvdd=='22':
            print("\n")
            print(request.form)
            print("variable 1",request.form['id_tpo_csa_nvdd_ge'])
            print("variable 2",lo_id_cntrto_bnfcro)
            print("\n")
            return self.crearnovedad('false', '2', request.form['id_tpo_csa_nvdd_ge'], la_id_cntrto, request.form['id_lgn_ge'], request.form['id_undd_ngco'], request.form['jstfccn'], request.form['id_grpo_emprsrl'], 'true', lo_id_cntrto_bnfcro, None, lc_cdgo_tpo_nvdd)
        elif lc_cdgo_tpo_nvdd=='1':
            #REACTIVACION DE CONTRATO
            return self.crearnovedad('true', '2', request.form['id_tpo_csa_nvdd_ge'], la_id_cntrto, request.form['id_lgn_ge'], request.form['id_undd_ngco'], request.form['jstfccn'], request.form['id_grpo_emprsrl'])
        else:
            print("esta en otro tipo de documento")



    def novedadescontratos(self):

        ln_id_scrsl = request.form['id_scrsl']
        lc_tpo_bsqda = request.form['tpo_bsqda']
        lc_cdgo_tpo_nvdd = request.form['cdgo_tpo_nvdd']

        if lc_tpo_bsqda=='1':
            #Contratos para Anulacion de contratos, inclusion de beneficiaios, retiro de beneficiarios, suspencion de beneficiarios
            strSql = " SELECT a.id AS id, "\
                " CASE WHEN(a.id_emprsa_une ISNULL) "\
                " 	THEN (j.cdgo || ' - ' || h.nmro_idntfccn) "\
                " 	ELSE (s.cdgo || ' - ' || q.nmro_idntfccn) "\
                " END AS idntfccn, "\
                " CASE WHEN(a.id_emprsa_une ISNULL) "\
                " 	THEN CONCAT_WS(' ', h.prmr_nmbre, h.sgndo_nmbre, h.prmr_aplldo, h.sgndo_aplldo) "\
                " 	ELSE (q.nmbre_rzn_scl) "\
                " END AS tmdr, "\
                " CONCAT((CASE k.dfne_prfjo_cntrto  "\
                " 	WHEN '0' THEN ' ' "\
                " 	WHEN '1' THEN k.prfjo_cntrto || '-' "\
                " 	WHEN '2' THEN k.prfjo_gnrl || '-' END), a.cnsctvo_cntrto::char(20)) AS cntrto, "\
                "   m.dscrpcn AS estdo_rgstro, "\
                "   c.dscrpcn AS pln, "\
                "   e.dscrpcn AS tpo_cntrto, "\
                " '' as id_tpo_csa_nvdd_ge, "\
                " '' as jstfccn "\
                " FROM "+dbConf.DB_SHMA+"tbcontratos a "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbplanes_une b ON a.id_pln_une = b.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbplanes c ON b.id_pln = c.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_contrato_une d ON a.id_tpo_cntrto_une = d.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_contrato e ON d.id_tpo_cntrto = e.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbusuarios_empresas_une f ON a.id_usro_emprsa_une = f.id "\
                " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios_une g ON f.id_usro_une = g.id "\
                " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios h ON g.id_usro = h.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion_ge i ON h.id_tpo_idntfccn_ge = i.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion j ON i.id_tpo_idntfccn = j.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbconsecutivos_internos  k ON a.id_cnsctvo_intrno = k.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbestadosregistros_ge l ON a.id_estdo_rgstro_ge = l.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbestadosregistros m ON l.id_estdo_rgstro = m.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbempresas_une p ON a.id_emprsa_une = p.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbempresas q ON p.id_emprsa = q.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion_ge r ON q.id_tpo_idntfccn_ge = r.id "\
                " LEFT OUTER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion s ON r.id_tpo_idntfccn = s.id "\
                " WHERE  a.estdo = true "\
                " AND a.id_scrsl = "+str(ln_id_scrsl)+" AND m.cdgo not in('6','7') "\
                " AND (a.id_emprsa_une IS NOT NULL "\
                " OR a.id_usro_emprsa_une IS NOT NULL); "
        else:

            strSql_rngo = " SELECT tpo_nvdd.cdgo, rngo_incl, rngo_fnl "\
                    " FROM "+dbConf.DB_SHMA+"tbtipos_novedades_ge tpo_nvdd_ge "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbtipos_novedades tpo_nvdd ON tpo_nvdd_ge.id_tpo_nvdd = tpo_nvdd.id "\
                    " WHERE tpo_nvdd.cdgo =  '"+str(lc_cdgo_tpo_nvdd)+"' and tpo_nvdd_ge.estdo = true LIMIT 1  "
            Cursor = self.lc_cnctn.queryFree(strSql_rngo)

            if Cursor :
                data = json.loads(json.dumps(Cursor[0], indent=2))
                ln_rngo_incl = data['rngo_incl']
                ln_rngo_fnl = data['rngo_fnl']
            else:
                ln_rngo_incl = 0
                ln_rngo_fnl = 0


            #//reactivacion  1, suspension 2, cancelacion 3
            #Se inicializa la variable nula
            add_var = ''
            add_var1 = ''
            if lc_cdgo_tpo_nvdd == '22': #Nuevo estado, DESVINCULACIÓN
                lc_and_estdo_cntrto =" b.cdgo IN('1','11') " #//Cancelacion de contratos Activos y suspendidos
                lc_case_condition = "AND (date (now())-  date (fctra.fcha_lmte_pgo)) BETWEEN  "+str(ln_rngo_incl)+" AND "+str(ln_rngo_fnl)+" "
                add_var = "select * from ( "
                add_var1 = " ) as data "\
                            " where (ds_mra > 0 AND estdo_rgstro = 'SUSPENDIDO') or estdo_rgstro = 'ACTIVO' "
            if lc_cdgo_tpo_nvdd == '1':
                lc_and_estdo_cntrto = " b.cdgo = '11' " #//Reactivacion de contratos suspendidos
                lc_case_condition = '';
            elif lc_cdgo_tpo_nvdd == '2':
                lc_and_estdo_cntrto =  " b.cdgo = '1' " #//Suspension de contratos activos
                lc_case_condition = "AND (date (now())-  date (fctra.fcha_lmte_pgo)) BETWEEN  "+str(ln_rngo_incl)+" AND "+str(ln_rngo_fnl)+" "
            elif lc_cdgo_tpo_nvdd == '3':
                lc_and_estdo_cntrto =" b.cdgo IN('1','11') " #//Cancelacion de contratos Activos y suspendidos
                lc_case_condition = "AND (date (now())-  date (fctra.fcha_lmte_pgo)) BETWEEN  "+str(ln_rngo_incl)+" AND "+str(ln_rngo_fnl)+" "
                add_var = "select * from ( "
                add_var1 = " ) as data "\
                            " where (ds_mra > 0 AND estdo_rgstro = 'SUSPENDIDO') or estdo_rgstro = 'ACTIVO' "

            #Contratos con días en mora
            strSql = add_var + " SELECT "\
                        " cntrto.id, "\
                        " CASE "\
                        	" WHEN fctra.id_emprsa_une IS NULL "\
                        	" THEN "\
                        	" CONCAT_WS(' ',tpo_idntfccn2.cdgo,'-',usro.nmro_idntfccn) "\
                        	" ELSE "\
                        	" CONCAT_WS(' ',tpo_idntfccn3.cdgo,'-',emprsa.nmro_idntfccn) "\
                        " END AS idntfccn, "\
                        " CASE "\
                        	" WHEN fctra.id_emprsa_une IS NULL "\
                        	" THEN "\
                        	" CONCAT_WS(' ', usro.prmr_aplldo, usro.sgndo_aplldo,usro.prmr_nmbre,usro.sgndo_nmbre) "\
                        	" ELSE "\
                        	" CONCAT_WS(' ', emprsa.nmbre_rzn_scl) "\
                        " END AS tmdr, "\
                        " CASE  cnsctvo_intrno.dfne_prfjo_cntrto "\
                        	" WHEN  '0' THEN '' "\
                        	" WHEN  '1' THEN CONCAT(cnsctvo_intrno.prfjo_cntrto,'-') "\
                        	" WHEN '2' THEN CONCAT(cnsctvo_intrno.prfjo_gnrl,'-') "\
                        " END || cntrto.cnsctvo_cntrto AS cntrto, "\
                        " b.dscrpcn as estdo_rgstro, "\
                        " pln.dscrpcn as pln, "\
                        " sb_pln.dscrpcn as sbpln, "\
                        " CASE WHEN sum(cf_crte.vlr_sldo) = 0 and sum(cf_crte.vlr_acmldo_cstgo)= 0 "\
                        " and sum(cf_crte.vlr_acmldo_prvsn) = 0 and sum(cf_crte.vlr_acmldo_rclsfccn)= 0 "\
                        " THEN "\
                        " '0' "\
                        " else "\
                        		" (SELECT "\
                        		" Max(DATE (now()) - DATE (fcha_lmte_pgo)) AS mora "\
                        		" FROM "\
                        		" "+dbConf.DB_SHMA+"tbcontratos "\
                        		" INNER JOIN "+dbConf.DB_SHMA+"tbcontratos_facturas_corte ON "+dbConf.DB_SHMA+"tbcontratos.id = "+dbConf.DB_SHMA+"tbcontratos_facturas_corte.id_cntrto "\
                        		" INNER JOIN "+dbConf.DB_SHMA+"tbfacturas ON "+dbConf.DB_SHMA+"tbfacturas.id = "+dbConf.DB_SHMA+"tbcontratos_facturas_corte.id_fctra "\
                        		" INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros_ge ON "+dbConf.DB_SHMA+"tbestadosregistros_ge.id = "+dbConf.DB_SHMA+"tbfacturas.id_estdo_rgstro_ge "\
                        		" INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros ON "+dbConf.DB_SHMA+"tbestadosregistros_ge.id_estdo_rgstro = "+dbConf.DB_SHMA+"tbestadosregistros.id "\
                        		" WHERE "\
                        		" "+dbConf.DB_SHMA+"tbcontratos.id = cntrto.ID "\
                        			" AND (vlr_sldo != 0 or vlr_acmldo_cstgo != 0	or vlr_acmldo_prvsn != 0 or vlr_acmldo_rclsfccn != 0) "\
                        			" AND (vlr_sldo > 0 or vlr_acmldo_cstgo > 0 or vlr_acmldo_prvsn> 0 or vlr_acmldo_rclsfccn> 0) "\
                        			" AND "\
                        			" "+dbConf.DB_SHMA+"tbestadosregistros.cdgo = '4' "\
                        		" GROUP BY "\
                        		" "+dbConf.DB_SHMA+"tbcontratos.cnsctvo_cntrto, "\
                        		" "+dbConf.DB_SHMA+"tbcontratos.id "\
                        		" ORDER BY mora DESC) "\
                        " END as ds_mra, "\
                        " '' as id_tpo_csa_nvdd_ge, "\
                        " '' as jstfccn "\
                        " FROM "+dbConf.DB_SHMA+"tbfacturas fctra "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbcontratos cntrto ON fctra.id_cntrto = cntrto.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbplanes_sub_une pln_sb_une ON cntrto.id_pln_sb_une = pln_sb_une.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbsubplanes_une sbpln_une ON pln_sb_une.id_sb_pln_une = sbpln_une.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbsubplanes sb_pln ON sbpln_une.id_sb_pln = sb_pln.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros_ge estdo_rgstro_ge ON fctra.id_estdo_rgstro_ge = estdo_rgstro_ge.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros  estdo_rgstro ON estdo_rgstro_ge.id_estdo_rgstro = estdo_rgstro.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbplanes_une pln_une ON cntrto.id_pln_une = pln_une.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbplanes pln ON pln_une.id_pln = pln.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbcontratos_facturas_corte cf_crte ON cf_crte.id_fctra = fctra.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros_ge a ON cntrto.id_estdo_rgstro_ge = a.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros  b ON a.id_estdo_rgstro = b.id "\
                        " INNER JOIN "+dbConf.DB_SHMA+"tbconsecutivos_internos cnsctvo_intrno ON cntrto.id_cnsctvo_intrno =cnsctvo_intrno.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios_empresas_une usro_emprsa_une ON cntrto.id_usro_emprsa_une = usro_emprsa_une.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios_une usro_une ON usro_emprsa_une.id_usro_une = usro_une.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios usro ON usro_une.id_usro = usro.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion_ge tpo_idntfccn_ge2 ON usro.id_tpo_idntfccn_ge = tpo_idntfccn_ge2.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion tpo_idntfccn2 ON tpo_idntfccn_ge2.id_tpo_idntfccn = tpo_idntfccn2.id "\
                        " LEFT JOIN "+dbConf.DB_SHMA+"tbempresas_une emprsa_une ON cntrto.id_emprsa_une = emprsa_une.id "\
                        " LEFT  JOIN "+dbConf.DB_SHMA+"tbempresas emprsa ON emprsa_une.id_emprsa = emprsa.id "\
                        " LEFT  JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion_ge tpo_idntfccn_ge3 ON emprsa.id_tpo_idntfccn_ge = tpo_idntfccn_ge3.id "\
                        " LEFT  JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion tpo_idntfccn3 ON tpo_idntfccn_ge3.id_tpo_idntfccn = tpo_idntfccn3.id "\
                        " WHERE fctra.estdo = true "\
                        " AND estdo_rgstro.cdgo = '4' "\
                        " AND pln_sb_une.estdo = true "\
                        " AND "+str(lc_and_estdo_cntrto)+" "\
                        " "+str(lc_case_condition)+" "\
                        " AND cntrto.id_scrsl = "+str(ln_id_scrsl)+" "\
                        " AND date(fctra.fcha_lmte_pgo) <= date(now()) "\
                        " and cntrto.id in (5,6,10,15,16) "\
                        " GROUP BY cntrto.id,cnsctvo_intrno.dfne_prfjo_cntrto,cnsctvo_intrno.prfjo_cntrto, "\
                        " cnsctvo_intrno.prfjo_gnrl, cntrto.cnsctvo_cntrto, sb_pln.dscrpcn,fctra.id_emprsa_une,tpo_idntfccn2.cdgo, "\
                        " usro.nmro_idntfccn,usro.prmr_aplldo,usro.sgndo_aplldo,usro.prmr_nmbre,usro.sgndo_nmbre, "\
                        " tpo_idntfccn3.cdgo,emprsa.nmro_idntfccn,emprsa.nmbre_rzn_scl,b.dscrpcn, pln.dscrpcn "\
                        " ORDER BY cntrto.id " + add_var1
        Cursor = self.lc_cnctn.queryFree(strSql)
        if Cursor :
            data = json.loads(json.dumps(Cursor, indent=2))
            return Utils.nice_json(data,200)
        else:
            return Utils.nice_json({labels.lbl_stts_success:labels.INFO_NO_DTS},202)

    def novedadescontratosbeneficiarios(self):

        ln_id_scrsl = request.form['id_scrsl']
        la_id_cntrto = request.form['id_prcso']
        la_data_cntrto = json.loads(la_id_cntrto)

        lc_cdna_cntrts = Utils.getObjetoACadenaIn(la_data_cntrto,"id")

        #Contratos para Anulacion de contratos, inclusion de beneficiaios, retiro de beneficiarios, suspencion de beneficiarios

        strSql = " SELECT "\
                    " cntrto_bnfcro.id as id_cntrto_bnfcro, "\
                    " trim(usro.nmro_idntfccn) AS nmro_idntfccn, "\
                    " CONCAT_WS(' ',trim(usro.prmr_aplldo),	trim(usro.sgndo_aplldo),	trim(usro.prmr_nmbre),trim(usro.sgndo_nmbre)) AS usro, "\
                    " '' as jstfccn, '' as id_tpo_csa_nvdd_ge, "\
                    " case when h.id_emprsa_une is null then "\
                    " 	CONCAT_WS(' ', k.prmr_nmbre, k.sgndo_nmbre, k.prmr_aplldo, k.sgndo_aplldo) "\
                    " else "\
                    " 	m.nmbre_rzn_scl "\
                    " end as ttlr, "\
                    " h.cnsctvo_cntrto as cntrto, h.id as id_cntrto "\
                    " FROM "+dbConf.DB_SHMA+"tbcontratos_beneficiarios cntrto_bnfcro "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbusuarios_empresas_une b ON cntrto_bnfcro.id_usro_emprsa_une = b.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbusuarios_une c ON b.id_usro_une = c.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbusuarios usro ON c.id_usro = usro.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion_ge e ON usro.id_tpo_idntfccn_ge = e.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbtipos_identificacion f ON e.id_tpo_idntfccn = f.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros_ge estdo_rgstro_ge ON cntrto_bnfcro.id_estdo_rgstro_ge = estdo_rgstro_ge.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbestadosregistros estdo_rgstro ON estdo_rgstro_ge.id_estdo_rgstro = estdo_rgstro.id "\
                    " INNER JOIN "+dbConf.DB_SHMA+"tbcontratos h on h.id = cntrto_bnfcro.id_cntrto "\
                    " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios_empresas_une i on h.id_usro_emprsa_une = i.id "\
                    " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios_une j on i.id_usro_une = j.id "\
                    " LEFT JOIN "+dbConf.DB_SHMA+"tbusuarios k on j.id_usro = k.id "\
                    " LEFT JOIN "+dbConf.DB_SHMA+"tbempresas_une l on h.id_emprsa_une = l.id "\
                    " LEFT JOIN "+dbConf.DB_SHMA+"tbempresas m on l.id_emprsa = m.id "\
                    " WHERE cntrto_bnfcro.id_cntrto in ("+str(lc_cdna_cntrts)+") "\
                    " AND cntrto_bnfcro.estdo = true "\
                    " AND estdo_rgstro.cdgo= '1' "\
                    " ORDER BY h.id, trim(usro.prmr_aplldo),trim(usro.sgndo_aplldo),trim(usro.prmr_nmbre),trim(usro.sgndo_nmbre) "
        Cursor = self.lc_cnctn.queryFree(strSql)
        if Cursor :
            data = json.loads(json.dumps(Cursor, indent=2))
            return Utils.nice_json(data,200)
        else:
            return Utils.nice_json({labels.lbl_stts_success:labels.INFO_NO_DTS},202)


    def crearnovedad(self, ll_aplca_intrgra, ln_id_prcso_tpo_une, ln_id_tpo_csa_nvdd_ge, ln_id_prcso, ln_id_lgn_ssn_ge, ln_id_undd_ngco, ln_jstfccn, ln_id_grpo_emprsrl, ll_estdo='true',ln_id_cntrto_bnfcro=None,lc_fcha_actl=None, lc_cdgo_tpo_nvdd = None):
        print("vrrrr",ln_id_cntrto_bnfcro)
        #Datos necesarios para crear el registro en Higia
        objectValues={}
        objectValues['id_prcso_tpo_une'] = str(ln_id_prcso_tpo_une)
        #####objectValues['id_tpo_csa_nvdd_ge'] = str(ln_id_tpo_csa_nvdd_ge)
        objectValues['id_lgn_crcn_ge'] = str(ln_id_lgn_ssn_ge)
        objectValues['id_lgn_mdfccn_ge'] = str(ln_id_lgn_ssn_ge)
        objectValues['estdo'] = ll_estdo

        #####objectValues['jstfccn'] = str(ln_jstfccn)

        if lc_cdgo_tpo_nvdd:
            #como este fue definido, entonces le asigno el id de este codigo a la variable ln_id_tpo_csa_nvdd_ge
            ln_id_tpo_csa_nvdd_ge = Utils.getIdTipoNovedad(lc_cdgo_tpo_nvdd)

        if not (lc_fcha_actl):
            lc_fcha_actl = time.ctime()

        objectValues['fcha_ocrrnca'] = lc_fcha_actl
        objectValues['fcha_crcn'] = lc_fcha_actl
        objectValues['fcha_mdfccn'] = lc_fcha_actl
        #if (ll_aplca_intrgra=='true' or ll_aplca_intrgra=='True'):
        la_data = {
            'pn_id_cntrto_bnfcro':ln_id_cntrto_bnfcro,
            'pd_fcha_actvcn':lc_fcha_actl,
            'pn_id_lgn_ssn_ge':ln_id_lgn_ssn_ge,
            'pn_id_tpo_csa_nvdd_ge':ln_id_tpo_csa_nvdd_ge,
            'pc_jstfccn':ln_jstfccn,
            'pc_idntfcdr':None,
            'pn_id_cntrto':ln_id_prcso,
            'pn_id_undd_ngco':ln_id_undd_ngco,
            'pn_id_grpo_emprsrl':ln_id_grpo_emprsrl,
            'pn_cdgo_tpo_nvdd':lc_cdgo_tpo_nvdd,
            }


        if (ll_aplca_intrgra=='true' or ll_aplca_intrgra=='True'):
            la_rsltdo_crr_intrgra = self.crear_integra(la_data)



        lc_trnsccn = ConnectDB()
        #lc_cnslta = ConnectDB()
        #lc_cnslta.beginTransaction()
        #####pc_cnnctDB.beginTransaction()

        if (ll_aplca_intrgra=='false' or ll_aplca_intrgra=='False'):
            ##LLAMADO A LA CREACION DE LA NOVEDAD DESDE HIGIA, CON MOVIMIENTOS DE OTRAS TABLAS CON NOVEDADES DIFERENTES A LAS QUE ESTABAN EN SSINTEGRA
            #####la_rsltdo_crr_intrgra = self.crear_higia(la_data)

            lc_cdgo_tpo_nvdd = Utils.getCodigoTipoNovedad(ln_id_tpo_csa_nvdd_ge)

            if lc_cdgo_tpo_nvdd == '22':




                '''
                *********************************************************************************************
                OJO, SE REPLICA LA FUNCION CREAR_HIGIA PARA PROBAR EL PROBLEMA CON LA TRANSACCIÓN
                *********************************************************************************************
                '''

                lc_fcha_actl = time.ctime()
                ln_id_estdo_rgstro_ge_cntrto = Utils.getIdEstdoRgstroGe('50')

                objNvdd={}
                objNvdd['fcha_ocrrnca'] = str(lc_fcha_actl)
                objNvdd['id_lgn_nvdd_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['id_lgn_crcn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['id_lgn_mdfccn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['fcha_crcn'] = str(lc_fcha_actl)
                objNvdd['fcha_mdfccn'] = str(lc_fcha_actl)
                objNvdd['id_undd_ngco'] = str(la_data['pn_id_undd_ngco'])
                #Se convierte el objeto json de contratos en una cadena separada por (,)
                lc_json_prcso = json.loads(la_data['pn_id_cntrto'])
                lc_in_id_cntrto = Utils.getObjetoACadenaIn(lc_json_prcso,"id",",")

                #inserto la novedad de RETIRO del contrato
                for obj in lc_json_prcso:
                    objNvdd['id_cntrto'] = str(obj['id'])
                    objNvdd['jstfccn'] = str(obj['jstfccn_cntrto'])
                    objNvdd['id_tpo_csa_nvdd_ge'] = str(obj['id_tpo_csa_nvdd_ge'])
                    id_nvdd_cntrto = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades_contratos",objNvdd, returnColumn = "id")

                objNvdd={}
                objNvdd['id_estdo_rgstro_ge'] = str(ln_id_estdo_rgstro_ge_cntrto)
                objNvdd['id_lgn_mdfccn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['fcha_mdfccn'] = lc_fcha_actl
                Cursor = lc_trnsccn.queryUpdate(dbConf.DB_SHMA+str('tbcontratos'), objNvdd,'id in ('+str(lc_in_id_cntrto)+')')

                #inserto la novedad de anulacion por cada beneficiario del contrato
                objNvdd={}
                objNvdd['fcha_ocrrnca'] = lc_fcha_actl
                objNvdd['id_lgn_nvdd_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['id_lgn_crcn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['id_lgn_mdfccn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['fcha_crcn'] = lc_fcha_actl
                objNvdd['fcha_mdfccn'] = lc_fcha_actl
                objNvdd['jstfccn'] = str(la_data['pc_jstfccn'])
                objNvdd['id_tpo_csa_nvdd_ge'] = str(la_data['pn_id_tpo_csa_nvdd_ge'])
                objNvdd['id_undd_ngco'] = str(la_data['pn_id_undd_ngco'])

                ##valido si la entrada de id_cntrto_bnfcro me llega con datos en json
                ##si es asi, entonces itero ese formato ingresando la informacion contenida en el json
                ln_id_cntrto_bnfcro = Utils.setIdContratoBeneficiario(ln_id_cntrto_bnfcro)
                lc_id_cntrts_bnfcrs_ge_en_nvdds = '' #Variable que sera usada en la aplicacion de las novedades para saber los respectivos  id y aplicar sus novedades en la tabla tbnovedades de higia
                #####################################################################################################################
                #Llego como una lista de Json, entonces se iteran
                print("\n ANTES DE LA FUNCION "+str(ln_id_cntrto_bnfcro)+" \n")
                if type(Utils.setIdContratoBeneficiario(ln_id_cntrto_bnfcro)) is list:

                    print("\n ENTRO AL setIdContratoBeneficiario "+str(ln_id_cntrto_bnfcro)+" \n")
                    for item_cntrto_bnfcro in ln_id_cntrto_bnfcro:
                        objNvdd['id_cntrto'] = str(item_cntrto_bnfcro['id_cntrto'])
                        objNvdd['id_cntrto_bnfcro'] = str(item_cntrto_bnfcro['id_cntrto_bnfcro'])
                        objNvdd['jstfccn'] = str(item_cntrto_bnfcro['jstfccn_cntrto_bnfcro'])
                        objNvdd['id_tpo_csa_nvdd_ge'] = str(item_cntrto_bnfcro['id_tpo_csa_nvdd_ge_bnfcro'])
                        id_cntrto_bnfcro = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades_contratos",objNvdd, returnColumn = "id")
                        ######FUNCIONA OK
                else:

                    if type(lc_json_prcso) is list:

                        for obj_cntro_bnfcro_cnslta in lc_json_prcso:

                            sql_dtlle = "  SELECT id_cntrto, id "\
                    			" FROM "+dbConf.DB_SHMA+"tbcontratos_beneficiarios "\
                    			" WHERE id_cntrto = "+str(obj_cntro_bnfcro_cnslta['id'])+" AND fcha_rtro IS NULL "
                            Cursor = lc_trnsccn.queryFree(sql_dtlle)
                            data_result = json.loads(json.dumps(Cursor, indent=2))
                            for obj_cntro in data_result:
                                lc_id_cntrts_bnfcrs_ge_en_nvdds = str(lc_id_cntrts_bnfcrs_ge_en_nvdds) + str(obj_cntro['id']) + ','
                                objNvdd['id_cntrto'] = str(obj_cntro['id_cntrto'])
                                objNvdd['id_cntrto_bnfcro'] = str(obj_cntro['id'])
                                objNvdd['id_tpo_csa_nvdd_ge'] = str(obj_cntro_bnfcro_cnslta['id_tpo_csa_nvdd_ge'])
                                objNvdd['jstfccn'] = str(obj_cntro_bnfcro_cnslta['jstfccn_cntrto'])
                                id_cntrto_bnfcro = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades_contratos",objNvdd, returnColumn = "id")

                #quito el (,) al final de la cadena
                lc_id_cntrts_bnfcrs_ge_en_nvdds = lc_id_cntrts_bnfcrs_ge_en_nvdds[0:len(lc_id_cntrts_bnfcrs_ge_en_nvdds)-1]
                #######################################################################################################################

                #Anulamos beneificiarios pero solo los que fcha_rtro sea = null
                objNvdd={}
                objNvdd['id_estdo_rgstro_ge'] = str(ln_id_estdo_rgstro_ge_cntrto)
                objNvdd['id_lgn_mdfccn_ge'] = str(la_data['pn_id_lgn_ssn_ge'])
                objNvdd['fcha_rtro'] = lc_fcha_actl
                objNvdd['fcha_mdfccn'] = lc_fcha_actl
                ##Si tiene contratos beneficiarios seleccionados, es necesario que actualice solo los contratos beneficiarios seleccionados, de lo contrario sigue el flujo normal
                if type(Utils.setIdContratoBeneficiario(ln_id_cntrto_bnfcro)) is list:
                    lc_id_cntrto_bnfcro_in = ' id in (' + Utils.getObjetoACadenaIn(ln_id_cntrto_bnfcro,"id_cntrto_bnfcro") + ') and '
                else:
                    lc_id_cntrto_bnfcro_in = ''

                Cursor =  lc_trnsccn.queryUpdate(dbConf.DB_SHMA+str('tbcontratos_beneficiarios'), objNvdd, str(lc_id_cntrto_bnfcro_in) + ' id_cntrto in ('+str(lc_in_id_cntrto)+') AND fcha_rtro IS NULL')
                ###### HASTA AQUI OK

                #si el usuario es standard (probable zona protegida) se debe actualizar el estado en "+dbConf.DB_SHMA+"tbusuarios_une
                check_sql = " SELECT b.id_usro_une as id_usro_une "\
                            " FROM "+dbConf.DB_SHMA+"tbcontratos a inner join "\
                            " "+dbConf.DB_SHMA+"tbusuarios_empresas_une b on a.id_usro_emprsa_une=b.id inner join "\
                            " "+dbConf.DB_SHMA+"tbusuarios_une c on b.id_usro_une=c.id "\
                            " WHERE a.id in ("+str(lc_in_id_cntrto)+") and c.aplca_usro_stndrd=true "
                Cursor = lc_trnsccn.queryFree(check_sql)
                #Obtngo un array Json con las opciones de perfil
                data = json.loads(json.dumps(Cursor, indent=2))
                for obj in data:
                    update_sql = " UPDATE "+dbConf.DB_SHMA+"tbusuarios_une "\
        				" SET id_estdo_rgstro_ge = "+str(ln_id_estdo_rgstro_ge_cntrto)+", id_lgn_mdfccn_ge = '"+str(la_data['pn_id_lgn_ssn_ge'])+"', fcha_mdfccn = now()  "\
        				" WHERE id = "+str(obj['id_usro_une'])+" "
                    lc_trnsccn.queryUpdateFree(update_sql)

                la_rsltdo_crr_intrgra = [True,'Novedad aplicada correctamente']


                '''
                ***************************************************************************************************************
                FIN   OJO, SE REPLICA LA FUNCION CREAR_HIGIA PARA PROBAR EL PROBLEMA CON LA TRANSACCIÓN  FIN DE LA FUNCION
                ***************************************************************************************************************
                '''
            else:
                la_rsltdo_crr_intrgra = [True,'Novedad aplicada correctamente']


        #lc_cnslta.endTransaction()
        #Si se genera satisfactoriamente, ejecutamos la transaccón de creacion del registro
        if(la_rsltdo_crr_intrgra[0]==True):
            #Se crea la novedad en Higia
            ##Si el contrato es una lista de contratos, entonces iteramos para fagregar cada contrato
            lc_json_prcso = json.loads(ln_id_prcso)
            if type(lc_json_prcso) is int:
                ## PROCESO DE ROBIN, QUE ENVIA SOLO UN VALOR NUMERICO REFERENTE AL PROCESO
                objectValues['id_prcso'] = str(ln_id_prcso)
                objectValues['jstfccn'] = str(ln_jstfccn)
                objectValues['id_tpo_csa_nvdd_ge'] = str(ln_id_tpo_csa_nvdd_ge)
                id_nvdd = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades",objectValues, returnColumn = "id")
            else:
                #INSERTA MULTIPLES PROCESOS QUE VIENEN DESDE UN JSON

                ##variables solo para usar en el insert de novedades cuanto no hay contratos beneficiarios seleccionados
                objectValues2 = {}
                objectValues2['id_prcso_tpo_une'] = str(ln_id_prcso_tpo_une)
                objectValues2['id_lgn_crcn_ge'] = str(ln_id_lgn_ssn_ge)
                objectValues2['id_lgn_mdfccn_ge'] = str(ln_id_lgn_ssn_ge)
                objectValues2['estdo'] = ll_estdo
                objectValues2['fcha_ocrrnca'] = lc_fcha_actl
                objectValues2['fcha_crcn'] = lc_fcha_actl
                objectValues2['fcha_mdfccn'] = lc_fcha_actl

                lc_json_prcso = json.loads(ln_id_prcso)
                for item in lc_json_prcso:
                    objectValues['id_prcso'] = str(item['id'])
                    objectValues['jstfccn'] = str(item['jstfccn_cntrto'])
                    objectValues['id_tpo_csa_nvdd_ge'] = str(item['id_tpo_csa_nvdd_ge'])
                    id_nvdd = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades",objectValues, returnColumn = "id")

                    ##Se insertan los contratos beneficiarios por cada iteracion del proceso en caso de que aplique
                    ## Ojo se le asigna a otra variable para que no la reescriba
                    if type(Utils.setIdContratoBeneficiario(ln_id_cntrto_bnfcro)) is str:
                        print("ENTRO EN LA CADENA VACIA IS STR")
                        ##Se insertan todos los contratos beneficiarios asociados al contratos
                        sql_dtlle22 = "  SELECT id_cntrto, id "\
                			" FROM "+dbConf.DB_SHMA+"tbcontratos_beneficiarios "\
                			" WHERE id_cntrto = "+str(item['id'])+" and id in (" + str(lc_id_cntrts_bnfcrs_ge_en_nvdds) + ")"
                        Cursor22 = lc_trnsccn.queryFree(sql_dtlle22)
                        data_result22 = json.loads(json.dumps(Cursor22, indent=2))
                        for obj_cntro_bnfcro in data_result22:
                            objectValues2['id_prcso'] = str(obj_cntro_bnfcro['id'])
                            objectValues2['jstfccn'] = str(item['jstfccn_cntrto'])
                            objectValues2['id_tpo_csa_nvdd_ge'] = str(item['id_tpo_csa_nvdd_ge'])
                            objectValues2['id_prcso_tpo_une'] = str(4)
                            id_nvdd = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades",objectValues2, returnColumn = "id")

                    ##Caso donde se ejecuta en ssintegra y por ende no tiene contratos beneficiarios seleccionados, NonType
                    if not ln_id_cntrto_bnfcro:
                        ##Se insertan todos los contratos beneficiarios asociados al contratos
                        sql_dtlle222 = "  SELECT id_cntrto, id "\
                			" FROM "+dbConf.DB_SHMA+"tbcontratos_beneficiarios "\
                			" WHERE id_cntrto = "+str(item['id'])+" and date(fcha_mdfccn) = date(now()) "
                        print("\n")
                        print("ENTRO EN EL NONE")
                        print("\n")

                        Cursor222 = lc_trnsccn.queryFree(sql_dtlle222)
                        data_result222 = json.loads(json.dumps(Cursor222, indent=2))
                        for obj_cntro_bnfcro222 in data_result222:
                            objectValues2['id_prcso'] = str(obj_cntro_bnfcro222['id'])
                            objectValues2['jstfccn'] = str(item['jstfccn_cntrto'])
                            objectValues2['id_tpo_csa_nvdd_ge'] = str(item['id_tpo_csa_nvdd_ge'])
                            objectValues2['id_prcso_tpo_une'] = str(4)
                            id_nvdd = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades",objectValues2, returnColumn = "id")


                ##Ahora se insertan las novedades por cada contrato beneficiario seleccionado
                #INSERTA MULTIPLES PROCESOS QUE VIENEN DESDE UN JSON
                if type(Utils.setIdContratoBeneficiario(ln_id_cntrto_bnfcro)) is list:
                    ##Se recorren todos los contratos beneficiarios seleccionados
                    for itemcntrtobnfcro in ln_id_cntrto_bnfcro:
                        objectValues['id_prcso'] = str(itemcntrtobnfcro['id_cntrto_bnfcro'])
                        objectValues['jstfccn'] = str(itemcntrtobnfcro['jstfccn_cntrto_bnfcro'])
                        objectValues['id_tpo_csa_nvdd_ge'] = str(itemcntrtobnfcro['id_tpo_csa_nvdd_ge_bnfcro'])
                        objectValues['id_prcso_tpo_une'] = str(4)
                        id_nvdd = lc_trnsccn.queryInsert(dbConf.DB_SHMA+"tbnovedades",objectValues, returnColumn = "id")


            #####pc_cnnctDB.endTransaction()
            ######DESCOMENTAR ESTA LINEA, SE COMENTA PARA REALIZAR PRUEBAS
            return Utils.nice_json({labels.lbl_stts_success:"Novedad Creada","id":str(id_nvdd)},200)
            ##return {labels.lbl_stts_success:"Novedad Creada","id":str(id_nvdd)} # <-- SE USA PARA LA PRUEBA UNITARIA, YA QUE NO INTERPRETA RESPUESTAS CON CABECERAS.
        else:
            #Si no se genera, se omite la transacción
            #####pc_cnnctDB.rollback()
            return Utils.nice_json({labels.lbl_stts_error:la_rsltdo_crr_intrgra[1]},400)

    def crear_higia(self,data):
        lc_fcha_actl = time.ctime()
        ln_id_estdo_rgstro_ge_cntrto = Utils.getIdEstdoRgstroGe('50')

        objectValues={}
        objectValues['fcha_ocrrnca'] = str(lc_fcha_actl)
        objectValues['id_lgn_nvdd_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['id_lgn_crcn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['id_lgn_mdfccn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['fcha_crcn'] = str(lc_fcha_actl)
        objectValues['fcha_mdfccn'] = str(lc_fcha_actl)
        objectValues['jstfccn'] = str(data['pc_jstfccn'])
        objectValues['id_tpo_csa_nvdd_ge'] = str(data['pn_id_tpo_csa_nvdd_ge'])
        objectValues['id_undd_ngco'] = str(data['pn_id_undd_ngco'])
        #Se convierte el objeto json de contratos en una cadena separada por (,)
        lc_json_prcso = json.loads(data['pn_id_cntrto'])
        lc_in_id_cntrto = Utils.getObjetoACadenaIn(lc_json_prcso,"id",",")

        #inserto la novedad de RETIRO del contrato
        for obj in lc_json_prcso:

            objectValues['id_cntrto'] = str(obj['id'])
            id_nvdd_cntrto = pc_cnnctDB.queryInsert(dbConf.DB_SHMA+"tbnovedades_contratos",objectValues, returnColumn = "id")

        objectValues={}
        objectValues['id_estdo_rgstro_ge'] = str(ln_id_estdo_rgstro_ge_cntrto)
        objectValues['id_lgn_mdfccn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['fcha_mdfccn'] = lc_fcha_actl
        Cursor = pc_cnnctDB.queryUpdate(dbConf.DB_SHMA+str('tbcontratos'), objectValues,'id in ('+str(lc_in_id_cntrto)+')')

        #inserto la novedad de anulacion por cada beneficiario del contrato
        objectValues={}
        objectValues['fcha_ocrrnca'] = lc_fcha_actl
        objectValues['id_lgn_nvdd_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['id_lgn_crcn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['id_lgn_mdfccn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['fcha_crcn'] = lc_fcha_actl
        objectValues['fcha_mdfccn'] = lc_fcha_actl
        objectValues['jstfccn'] = str(data['pc_jstfccn'])
        objectValues['id_tpo_csa_nvdd_ge'] = str(data['pn_id_tpo_csa_nvdd_ge'])
        objectValues['id_undd_ngco'] = str(data['pn_id_undd_ngco'])
        sql_dtlle = "  SELECT id_cntrto, id "\
			" FROM "+dbConf.DB_SHMA+"tbcontratos_beneficiarios "\
			" WHERE id_cntrto in ("+str(lc_in_id_cntrto)+") AND fcha_rtro IS NULL "
        Cursor = pc_cnnctDB.queryFree(sql_dtlle)
        data_result = json.loads(json.dumps(Cursor, indent=2))
        for obj_cntro in data_result:
            objectValues['id_cntrto'] = str(obj_cntro['id_cntrto'])
            objectValues['id_cntrto_bnfcro'] = str(obj_cntro['id'])
            id_cntrto_bnfcro = pc_cnnctDB.queryInsert(dbConf.DB_SHMA+"tbnovedades_contratos",objectValues, returnColumn = "id")

        #Anulamos beneificiarios pero solo los que fcha_rtro sea = null
        objectValues={}
        objectValues['id_estdo_rgstro_ge'] = str(ln_id_estdo_rgstro_ge_cntrto)
        objectValues['id_lgn_mdfccn_ge'] = str(data['pn_id_lgn_ssn_ge'])
        objectValues['fcha_rtro'] = lc_fcha_actl
        objectValues['fcha_mdfccn'] = lc_fcha_actl

        Cursor =  pc_cnnctDB.queryUpdate(dbConf.DB_SHMA+str('tbcontratos_beneficiarios'), objectValues,'id_cntrto in ('+str(lc_in_id_cntrto)+') AND fcha_rtro IS NULL')

        #si el usuario es standard (probable zona protegida) se debe actualizar el estado en "+dbConf.DB_SHMA+"tbusuarios_une
        check_sql = " SELECT b.id_usro_une as id_usro_une "\
                    " FROM "+dbConf.DB_SHMA+"tbcontratos a inner join "\
                    " "+dbConf.DB_SHMA+"tbusuarios_empresas_une b on a.id_usro_emprsa_une=b.id inner join "\
                    " "+dbConf.DB_SHMA+"tbusuarios_une c on b.id_usro_une=c.id "\
                    " WHERE a.id in ("+str(lc_in_id_cntrto)+") and c.aplca_usro_stndrd=true "
        Cursor = pc_cnnctDB.queryFree(check_sql)
        #Obtngo un array Json con las opciones de perfil
        data = json.loads(json.dumps(Cursor, indent=2))
        for obj in data:
            update_sql = " UPDATE "+dbConf.DB_SHMA+"tbusuarios_une "\
				" SET id_estdo_rgstro_ge = "+str(ln_id_estdo_rgstro_ge_cntrto)+", id_lgn_mdfccn_ge = '"+str(data['pn_id_lgn_ssn_ge'])+"', fcha_mdfccn = now()  "\
				" WHERE id = "+str(obj['id_usro_une'])+" "
            pc_cnnctDB.queryUpdateFree(update_sql)

        return [True,'Novedad aplicada correctamente']
